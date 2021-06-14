resource "aws_lambda_function" "dispatcher" {
  function_name    = substr("${local.project}-dispatcher${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_dispatcher.output_path
  source_code_hash = data.archive_file.lambda_dispatcher.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_params.runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_params.memory_size
  timeout          = var.lambda_params.timeout
  publish          = true
  tags             = local.tags
  layers           = [module.py37_datapump_020.layer_arn, var.rasterio_lambda_layer_arn]
  environment {
    variables = {
      ENV                           = var.environment
      DATA_API_URI                  = var.data_api_uri
      S3_BUCKET_PIPELINE            = var.pipelines_bucket
      S3_BUCKET_DATA_LAKE           = var.data_lake_bucket
      DATAPUMP_TABLE_NAME           = aws_dynamodb_table.datapump.name
      S3_GLAD_PATH                  = var.glad_path
    }
  }
}

resource "aws_lambda_function" "executor" {
  function_name    = substr("${local.project}-executor${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_executor.output_path
  source_code_hash = data.archive_file.lambda_executor.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_params.runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_params.memory_size
  timeout          = var.lambda_params.timeout
  publish          = true
  tags             = local.tags
  layers           = [module.py37_datapump_020.layer_arn]
  environment {
    variables = {
      ENV                            = var.environment
      S3_BUCKET_PIPELINE             = var.pipelines_bucket
      S3_BUCKET_DATA_LAKE            = var.data_lake_bucket
      GEOTRELLIS_JAR_PATH            = var.geotrellis_jar_path
      PUBLIC_SUBNET_IDS              = jsonencode(var.public_subnet_ids)
      EC2_KEY_NAME                   = var.ec2_key_name
      EMR_SERVICE_ROLE               = var.emr_service_role_name
      EMR_INSTANCE_PROFILE           = var.emr_instance_profile_name
      COMMAND_RUNNER_JAR             = var.command_runner_jar
      DATA_API_URI                   = var.data_api_uri
    }
  }
}

resource "aws_lambda_function" "postprocessor" {
  function_name    = substr("${local.project}-postprocessor${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_postprocessor.output_path
  source_code_hash = data.archive_file.lambda_postprocessor.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_params.runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_params.memory_size
  timeout          = var.lambda_params.timeout
  publish          = true
  tags             = local.tags
  layers           = [module.py37_datapump_020.layer_arn, var.rasterio_lambda_layer_arn]
  environment {
    variables = {
      ENV                            = var.environment
      S3_BUCKET_PIPELINE             = var.pipelines_bucket
      S3_BUCKET_DATA_LAKE            = var.data_lake_bucket
      DATA_API_URI                   = var.data_api_uri
      DATAPUMP_TABLE_NAME            = aws_dynamodb_table.datapump.name
    }
  }
}

resource "aws_lambda_function" "fastapi" {
  function_name    = substr("${local.project}-fastapi${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_fastapi.output_path
  source_code_hash = data.archive_file.lambda_fastapi.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_params.runtime
  handler          = "lambda_function.handler"
  memory_size      = 512
  timeout          = var.lambda_params.timeout
  publish          = true
  tags             = local.tags
  layers           = [data.terraform_remote_state.lambda_layers.outputs.py37_fastapi_0652_arn]
  environment {
    variables = {
      ENV                            = var.environment
      S3_BUCKET_PIPELINE             = var.pipelines_bucket
      S3_BUCKET_DATA_LAKE            = var.data_lake_bucket
      DATA_API_URI                   = var.data_api_uri
    }
  }
}