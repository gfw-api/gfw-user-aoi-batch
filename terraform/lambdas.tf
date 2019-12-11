resource "aws_lambda_function" "submit_job" {
  function_name    = substr("${local.project}-submit_job${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_submit_job.output_path
  source_code_hash = data.archive_file.lambda_submit_job.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_submit_job_runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_submit_job_memory_size
  timeout          = var.lambda_submit_job_timeout
  publish          = true
  tags             = local.tags
  layers           = [module.lambda_layers.datapump_utils_arn]
  environment {
    variables = {
      ENV                = var.environment
      S3_BUCKET_PIPELINE = data.terraform_remote_state.core.outputs.pipelines_bucket
      GEOTRELLIS_JAR     = var.geotrellis_jar
    }
  }
}

resource "aws_lambda_function" "upload_results_to_datasets" {
  function_name    = substr("${local.project}-upload_results_to_datasets${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_upload_results_to_datasets.output_path
  source_code_hash = data.archive_file.lambda_upload_results_to_datasets.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_upload_results_runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_upload_results_memory_size
  timeout          = var.lambda_upload_results_timeout
  publish          = true
  tags             = local.tags
  layers           = [module.lambda_layers.datapump_utils_arn]
  environment {
    variables = {
      ENV = var.environment
    }
  }
}

resource "aws_lambda_function" "check_datasets_saved" {
  function_name    = substr("${local.project}-check_datasets_saved${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_check_datasets_saved.output_path
  source_code_hash = data.archive_file.lambda_check_datasets_saved.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_check_datasets_runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_check_datasets_memory_size
  timeout          = var.lambda_check_datasets_timeout
  publish          = true
  tags             = local.tags
  layers           = [module.lambda_layers.datapump_utils_arn]
  environment {
    variables = {
      ENV = var.environment
    }
  }
}

resource "aws_lambda_function" "check_new_aoi" {
  function_name    = substr("${local.project}-check_new_aoi${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_check_new_aoi.output_path
  source_code_hash = data.archive_file.lambda_check_new_aoi.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_check_new_aoi_runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_check_new_aoi_memory_size
  timeout          = var.lambda_check_new_aoi_timeout
  publish          = true
  tags             = local.tags
  layers           = [module.lambda_layers.datapump_utils_arn, data.terraform_remote_state.core.outputs.lambda_layer_shapely_pyyaml_arn]
  environment {
    variables = {
      ENV                = var.environment
      S3_BUCKET_PIPELINE = data.terraform_remote_state.core.outputs.pipelines_bucket
      S3_BUCKET_DATALAKE = data.terraform_remote_state.core.outputs.data-lake_bucket
    }
  }
}

resource "aws_lambda_function" "update_new_aoi_statuses" {
  function_name    = substr("${local.project}-update_new_aoi_statuses${local.name_suffix}", 0, 64)
  filename         = data.archive_file.lambda_update_new_aoi_statuses.output_path
  source_code_hash = data.archive_file.lambda_update_new_aoi_statuses.output_base64sha256
  role             = aws_iam_role.datapump_lambda.arn
  runtime          = var.lambda_update_new_aoi_statuses_runtime
  handler          = "lambda_function.handler"
  memory_size      = var.lambda_update_new_aoi_statuses_memory_size
  timeout          = var.lambda_update_new_aoi_statuses_timeout
  publish          = true
  tags             = local.tags
  layers           = [module.lambda_layers.datapump_utils_arn]
  environment {
    variables = {
      ENV                = var.environment
      S3_BUCKET_PIPELINE = data.terraform_remote_state.core.outputs.pipelines_bucket
    }
  }
}