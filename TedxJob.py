import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join, struct

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

##### FROM FILES
tedx_dataset_path = "s3://tests3bucketgb/final_list.csv"

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()

glueContext = GlueContext(sc)
spark = glueContext.spark_session

job = Job(glueContext)
job.init(args['JOB_NAME'], args)

#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(tedx_dataset_path)

tedx_dataset.printSchema()

#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("id is not null").count()

print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")

## READ THE DETAILS
details_dataset_path = "s3://tests3bucketgb/details.csv"
details_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(details_dataset_path)

details_dataset = details_dataset.select(col("id").alias("id_ref"),
                                         col("description"),
                                         col("duration"),
                                         col("publishedAt"))

# AND JOIN WITH THE MAIN TABLE
tedx_dataset_main = tedx_dataset.join(details_dataset, tedx_dataset.id == details_dataset.id_ref, "left") \
    .drop("id_ref")

tedx_dataset_main.printSchema()

## READ TAGS DATASET
tags_dataset_path = "s3://tests3bucketgb/tags.csv"
tags_dataset = spark.read.option("header", "true").csv(tags_dataset_path)

# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("id").alias("id_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset_main.join(tags_dataset_agg, tedx_dataset.id == tags_dataset_agg.id_ref, "left") \
    .drop("id_ref") \
    .select(col("id").alias("_id"), col("*")) \
    .drop("id")

tedx_dataset_agg.printSchema()

## READ RELATED VIDEO DATASET
related_video_dataset_path = "s3://tests3bucketgb/related_videos.csv"
related_video_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(related_video_dataset_path)

# AGGREGATE RELATED VIDEOS BY ID
related_video_agg = related_video_dataset.groupBy(col("id").alias("id_ref")).agg(
    collect_list(
        struct(
            col("related_id").alias("relatedId"),
            col("slug"),
            col("title"),
            col("duration"),
            col("viewedCount"),
            col("presenterDisplayName").alias("presenter")
        )
    ).alias("relatedVideos")
)

related_video_agg.printSchema()

# JOIN RELATED VIDEOS WITH THE MAIN DATASET
tedx_dataset_final = tedx_dataset_agg.join(related_video_agg, tedx_dataset_agg._id == related_video_agg.id_ref, "left") \
    .drop("id_ref")

tedx_dataset_final.printSchema()

## READ FINAL TRANSCRIPTS DATASET
transcripts_dataset_path = "s3://tests3bucketgb/final_with_transcripts_10.csv"

transcripts_dataset = spark.read \
    .option("header", "true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(transcripts_dataset_path)

transcripts_dataset = transcripts_dataset.select(
    col("id").alias("id_ref"),
    col("transcript")
)

# JOIN TRANSCRIPTS WITH MAIN DATASET
tedx_dataset_final = tedx_dataset_final.join(transcripts_dataset, tedx_dataset_final._id == transcripts_dataset.id_ref, "left") \
    .drop("id_ref")

# WRITE TO MONGODB
write_mongo_options = {
    "connectionName": "TEDX",
    "database": "unibg_tedx_2025",
    "collection": "tedx_data",
    "ssl": "true",
    "ssl.domain_match": "false"
}

from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_final, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)