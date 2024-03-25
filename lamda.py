 Lambda for Ingestion :
  python
   import boto3
   
   s3_client = boto3.client('s3')
   
   def lambda_handler(event, context):
       # Code to fetch raw data and store it in S3 bucket
       # Replace this with your actual code to fetch and upload raw data
       s3_client.upload_file('raw_data.csv', 's3-bucket', 'raw_data/raw_data.csv')