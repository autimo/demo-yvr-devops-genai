terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {}
}

# Configure the AWS provider
provider "aws" {
  region = "us-west-2"
}

locals {
  runtime = "python3.12"
}

# Create a secure string parameter for the OpenAI API key
resource "aws_ssm_parameter" "openai_api_key" {
  name        = "openai-api-key"
  description = "OpenAI API key for the Issue Creator Lambda function"
  type        = "SecureString"
  value       = var.openai_api_key
}

# Create a secure string parameter for the GitHub access token
resource "aws_ssm_parameter" "github_access_token" {
  name        = "github-access-token"
  description = "GitHub access token for the Issue Creator Lambda function"
  type        = "SecureString"
  value       = var.github_access_token
}

# Create a Lambda layer for the Discord bot dependencies
resource "null_resource" "discord_bot_dependencies" {
  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/out/discord_bot_dependencies/python && pip3 install --target ${path.module}/out/discord_bot_dependencies/python -r ${path.module}/../src/discord_bot/requirements.txt"
  }
}

data "archive_file" "discord_bot_dependencies" {
  type        = "zip"
  source_dir  = "${path.module}/out/discord_bot_dependencies"
  output_path = "${path.module}/out/discord_bot_dependencies.zip"

  depends_on = [null_resource.discord_bot_dependencies]
}

resource "aws_lambda_layer_version" "discord_bot_dependencies" {
  filename            = data.archive_file.discord_bot_dependencies.output_path
  layer_name          = "discord-bot-dependencies"
  compatible_runtimes = [local.runtime]
  source_code_hash    = data.archive_file.discord_bot_dependencies.output_base64sha256
}

# Create a Lambda layer for the Issue Creator dependencies
resource "null_resource" "issue_creator_dependencies" {
  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/out/issue_creator_dependencies/python && pip3 install --target ${path.module}/out/issue_creator_dependencies/python -r ${path.module}/../src/issue_creator/requirements.txt"
  }
}

data "archive_file" "issue_creator_dependencies" {
  type        = "zip"
  source_dir  = "${path.module}/out/issue_creator_dependencies"
  output_path = "${path.module}/out/issue_creator_dependencies.zip"

  depends_on = [null_resource.issue_creator_dependencies]
}

resource "aws_lambda_layer_version" "issue_creator_dependencies" {
  filename            = data.archive_file.issue_creator_dependencies.output_path
  layer_name          = "issue-creator-dependencies"
  compatible_runtimes = [local.runtime]
  source_code_hash    = data.archive_file.issue_creator_dependencies.output_base64sha256
}

# Create a Lambda function for the Discord bot
data "archive_file" "discord_bot" {
  type        = "zip"
  source_dir  = "${path.module}/../src/discord_bot"
  output_path = "${path.module}/out/discord_bot.zip"
}

resource "aws_lambda_function" "discord_bot" {
  filename         = data.archive_file.discord_bot.output_path
  function_name    = "discord-bot"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.lambda_handler"
  runtime          = local.runtime
  source_code_hash = filebase64sha256(data.archive_file.discord_bot.output_path)
  layers           = [aws_lambda_layer_version.discord_bot_dependencies.arn]

  environment {
    variables = {
      DISCORD_PUBLIC_KEY = var.discord_bot_public_key
    }
  }

  tags = {
    # This is used by the issue creator lambda to create issues on the repo
    "github-repo" = var.discord_bot_repo_url
  }
}

# Create the API Gateway to trigger the Discord bot Lambda
resource "aws_api_gateway_rest_api" "discord_bot_api" {
  name        = "DiscordBotAPI"
  description = "API Gateway for the Discord Bot Lambda Function"
}

resource "aws_api_gateway_resource" "discord_bot_resource" {
  rest_api_id = aws_api_gateway_rest_api.discord_bot_api.id
  parent_id   = aws_api_gateway_rest_api.discord_bot_api.root_resource_id
  path_part   = "interactions"
}

resource "aws_api_gateway_method" "discord_bot_method" {
  rest_api_id   = aws_api_gateway_rest_api.discord_bot_api.id
  resource_id   = aws_api_gateway_resource.discord_bot_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "discord_bot_integration" {
  rest_api_id = aws_api_gateway_rest_api.discord_bot_api.id
  resource_id = aws_api_gateway_resource.discord_bot_resource.id
  http_method = aws_api_gateway_method.discord_bot_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.discord_bot.invoke_arn
}

resource "aws_api_gateway_deployment" "discord_bot_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.discord_bot_api.id

  # Ensure the deployment gets updated when the API changes
  triggers = {
    redeployment = sha1(jsonencode({
      rest_api    = aws_api_gateway_rest_api.discord_bot_api.body,
      resource    = aws_api_gateway_resource.discord_bot_resource.path_part,
      method      = aws_api_gateway_method.discord_bot_method.http_method,
      integration = aws_api_gateway_integration.discord_bot_integration.uri,
    }))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "discord_bot_api_stage" {
  deployment_id = aws_api_gateway_deployment.discord_bot_api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.discord_bot_api.id
  stage_name    = "api"
}


resource "aws_lambda_permission" "discord_bot_api" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_bot.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.discord_bot_api.execution_arn}/*/*"
}

# Create the Issue Creator Lambda function
data "archive_file" "issue_creator" {
  type        = "zip"
  source_dir  = "${path.module}/../src/issue_creator"
  output_path = "${path.module}/out/issue_creator.zip"
}

resource "aws_lambda_function" "issue_creator" {
  filename         = data.archive_file.issue_creator.output_path
  function_name    = "issue-creator"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "main.lambda_handler"
  runtime          = local.runtime
  source_code_hash = filebase64sha256(data.archive_file.issue_creator.output_path)
  layers           = [aws_lambda_layer_version.issue_creator_dependencies.arn]
  timeout          = 60

  environment {
    variables = {
      OPENAI_API_KEY_SSM_PARAM      = aws_ssm_parameter.openai_api_key.name
      GITHUB_ACCESS_TOKEN_SSM_PARAM = aws_ssm_parameter.github_access_token.name
    }
  }
}

# Create IAM role for Lambda execution
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach necessary permissions to the Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_exec.name
}

# Grant permission to the Issue Creator Lambda to call get_function
resource "aws_iam_policy" "lambda_get_function_policy" {
  name        = "LambdaGetFunctionPolicy"
  description = "Allows lambda function to call get_function on other lambda functions"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:GetFunction",
          "lambda:ListTags"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_get_function_policy_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_get_function_policy.arn
}

# Create CloudWatch Log Group for the Discord bot
resource "aws_cloudwatch_log_group" "discord_bot_logs" {
  name              = "/aws/lambda/discord-bot"
  retention_in_days = 14
}

# Allow the CloudWatch Logs to invoke the Issue Creator Lambda function
resource "aws_lambda_permission" "cloudwatch_to_issue_creator" {
  statement_id  = "AllowExecutionFromCloudWatchLogs"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.issue_creator.function_name
  principal     = "logs.amazonaws.com"
  source_arn    = "${aws_cloudwatch_log_group.discord_bot_logs.arn}:*"
}

# Create CloudWatch Log Group subscription filter
resource "aws_cloudwatch_log_subscription_filter" "issue_creator_trigger" {
  name            = "issue-creator-trigger"
  log_group_name  = aws_cloudwatch_log_group.discord_bot_logs.name
  filter_pattern  = "ERROR"
  destination_arn = aws_lambda_function.issue_creator.arn

  depends_on = [aws_lambda_permission.cloudwatch_to_issue_creator]
}

# Grant permission to the Issue Creator Lambda to read the OpenAI API key and GitHub access token from SSM Parameter Store
resource "aws_iam_policy" "issue_creator_read_ssm_policy" {
  name        = "IssueCreatorReadSSMPolicy"
  description = "Allows the Issue Creator Lambda function to read the OpenAI API key and GitHub access token from SSM Parameter Store"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter"
        ]
        Effect = "Allow"
        Resource = [
          aws_ssm_parameter.openai_api_key.arn,
          aws_ssm_parameter.github_access_token.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "issue_creator_read_ssm_policy_attachment" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.issue_creator_read_ssm_policy.arn
}
