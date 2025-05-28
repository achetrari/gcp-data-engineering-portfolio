import pandas as pd
import requests
from google.cloud import storage, bigquery
from datetime import datetime
import os
import sys

class CovidDataPipeline:
    def __init__(self, project_id="data-engineering-bootcamp"):
        self.project_id = project_id
        self.bucket_name = "data-eng-bootcamp-covid-raw"
        
        # Initialize clients
        try:
            self.storage_client = storage.Client(project=project_id)
            self.bq_client = bigquery.Client(project=project_id)
            print(f"✅ Connected to GCP project: {project_id}")
        except Exception as e:
            print(f"❌ Failed to connect to GCP: {e}")
            sys.exit(1)
    
    def test_connections(self):
        """Test GCP connections"""
        print("🔍 Testing GCP connections...")
        
        # Test BigQuery
        try:
            datasets = list(self.bq_client.list_datasets())
            print(f"✅ BigQuery: Found {len(datasets)} datasets")
        except Exception as e:
            print(f"❌ BigQuery connection failed: {e}")
            return False
            
        # Test Cloud Storage
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                print(f"⚠️  Bucket {self.bucket_name} doesn't exist, creating...")
                bucket.create()
            print(f"✅ Cloud Storage: Bucket {self.bucket_name} accessible")
        except Exception as e:
            print(f"❌ Cloud Storage connection failed: {e}")
            return False
            
        return True
    
    def download_covid_data(self):
        """Download COVID data from Our World in Data"""
        print("📥 Downloading COVID data...")
        
        url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
        
        try:
            # Download with progress indication
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Read into pandas
            df = pd.read_csv(url)
            
            # Basic validation
            print(f"📊 Downloaded {len(df):,} records")
            print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"🌍 Countries: {df['location'].nunique()}")
            
            # Data quality checks
            missing_data = df.isnull().sum().sum()
            print(f"🔍 Missing values: {missing_data:,}")
            
            return df
            
        except Exception as e:
            print(f"❌ Failed to download data: {e}")
            return None
    
    def upload_to_storage(self, df):
        """Upload data to Cloud Storage"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"covid_data_{timestamp}.csv"
        
        print(f"☁️  Uploading to Cloud Storage: {filename}")
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"raw/{filename}")
            
            # Convert to CSV and upload
            csv_data = df.to_csv(index=False)
            blob.upload_from_string(csv_data, content_type='text/csv')
            
            gcs_uri = f"gs://{self.bucket_name}/raw/{filename}"
            print(f"✅ Uploaded to: {gcs_uri}")
            
            return gcs_uri, filename
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None, None
    
    def create_bigquery_tables(self):
        """Create BigQuery tables with proper schema"""
        print("🏗️  Creating BigQuery tables...")
        
        # Schema for COVID data
        schema = [
            bigquery.SchemaField("iso_code", "STRING"),
            bigquery.SchemaField("continent", "STRING"),
            bigquery.SchemaField("location", "STRING"),
            bigquery.SchemaField("date", "DATE"),
            bigquery.SchemaField("total_cases", "FLOAT"),
            bigquery.SchemaField("new_cases", "FLOAT"),
            bigquery.SchemaField("total_deaths", "FLOAT"),
            bigquery.SchemaField("new_deaths", "FLOAT"),
            bigquery.SchemaField("total_vaccinations", "FLOAT"),
            bigquery.SchemaField("people_vaccinated", "FLOAT"),
            bigquery.SchemaField("people_fully_vaccinated", "FLOAT"),
            bigquery.SchemaField("population", "FLOAT"),
        ]
        
        table_id = f"{self.project_id}.covid_staging.raw_covid_data"
        
        try:
            table = bigquery.Table(table_id, schema=schema)
            table = self.bq_client.create_table(table, exists_ok=True)
            print(f"✅ Created table: {table_id}")
            return table_id
        except Exception as e:
            print(f"❌ Failed to create table: {e}")
            return None
    
    def load_to_bigquery(self, gcs_uri, table_id):
        """Load data from GCS to BigQuery"""
        print(f"📊 Loading data to BigQuery: {table_id}")
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            allow_quoted_newlines=True,
            allow_jagged_rows=True
        )
        
        try:
            load_job = self.bq_client.load_table_from_uri(
                gcs_uri, table_id, job_config=job_config
            )
            
            # Wait for job to complete
            load_job.result()
            
            # Get table info
            table = self.bq_client.get_table(table_id)
            print(f"✅ Loaded {table.num_rows:,} rows to {table_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ BigQuery load failed: {e}")
            return False
    
    def run_data_quality_checks(self):
        """Run basic data quality checks"""
        print("🔍 Running data quality checks...")
        
        queries = {
            "Total Records": "SELECT COUNT(*) as count FROM `data-engineering-bootcamp.covid_staging.raw_covid_data`",
            "Date Range": """
                SELECT 
                    MIN(date) as min_date, 
                    MAX(date) as max_date 
                FROM `data-engineering-bootcamp.covid_staging.raw_covid_data`
            """,
            "Top 5 Countries by Cases": """
                SELECT 
                    location,
                    MAX(total_cases) as max_cases
                FROM `data-engineering-bootcamp.covid_staging.raw_covid_data`
                WHERE location != 'World' AND continent IS NOT NULL
                GROUP BY location
                ORDER BY max_cases DESC
                LIMIT 5
            """
        }
        
        for check_name, query in queries.items():
            try:
                result = self.bq_client.query(query).result()
                print(f"\n📋 {check_name}:")
                for row in result:
                    print(f"   {dict(row)}")
            except Exception as e:
                print(f"❌ Quality check '{check_name}' failed: {e}")
    
    def run_pipeline(self):
        """Execute the complete pipeline"""
        print("🚀 Starting COVID Data Pipeline...")
        print("=" * 50)
        
        try:
            # Step 1: Test connections
            if not self.test_connections():
                return False
            
            # Step 2: Download data
            df = self.download_covid_data()
            if df is None:
                return False
            
            # Step 3: Upload to storage
            gcs_uri, filename = self.upload_to_storage(df)
            if gcs_uri is None:
                return False
            
            # Step 4: Create BigQuery tables
            table_id = self.create_bigquery_tables()
            if table_id is None:
                return False
            
            # Step 5: Load to BigQuery
            if not self.load_to_bigquery(gcs_uri, table_id):
                return False
            
            # Step 6: Data quality checks
            self.run_data_quality_checks()
            
            print("\n🎉 Pipeline completed successfully!")
            print(f"📊 Data available in: {table_id}")
            print(f"☁️  Raw data in: {gcs_uri}")
            
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            return False

def main():
    """Main execution function"""
    pipeline = CovidDataPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n✅ Ready for Week 1 data transformations!")
    else:
        print("\n❌ Pipeline failed - check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()