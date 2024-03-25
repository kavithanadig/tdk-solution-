import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import count
from pyspark.sql.types import StringType, StructField, StructType

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Load data from Glue Data Catalog
datasource0 = glueContext.create_dynamic_frame.from_catalog(database="tdkl2", table_name="tdkl2")

# Convert DynamicFrame to DataFrame for easier processing
df = datasource0.toDF()

# Print the schema of the DataFrame to identify column names
df.printSchema()

# Adjust column names based on the schema
# Ensure to replace "response" with the correct column name

# Count distinct users (based on IP addresses)
num_users = df.select("col0").distinct().count()

# Count number of requests per user
requests_per_user = df.groupBy("col0").agg(count("*").alias("requests_per_user"))

# Display total number of successful requests
# If the column name for response code is different, replace "response" accordingly
num_successful_requests = df.filter(df["col0"] == 200).count()

# Create schema for the final DataFrame
schema = StructType([
    StructField("metric", StringType(), True),
    StructField("value", StringType(), True)
])

# Create DataFrame with results
results = spark.createDataFrame([
    ("Number of users", str(num_users)),
    ("Total number of successful requests", str(num_successful_requests))
], schema)

# Convert requests_per_user DataFrame to Pandas DataFrame
requests_per_user_pd = requests_per_user.toPandas()

# Add "Requests per user" as a separate row in the results DataFrame
requests_per_user_str = requests_per_user_pd.apply(lambda x: ("Requests per user: " + x["col0"], str(x["requests_per_user"])), axis=1)
requests_per_user_df = spark.createDataFrame(requests_per_user_str, schema)

# Combine all DataFrames
final_results = results.union(requests_per_user_df)

# Write final results to CSV file in S3
output_path = "s3://tdkl2/output/"
final_results.write.mode("overwrite").csv(output_path + "results", header=True)
