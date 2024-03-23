# Demo YVR DevOps GenAI Project

Welcome to the Demo YVR DevOps GenAI Project!

This repository contains the source code for a Discord bot and an Issue Creator Lambda function, both of which are designed to showcase the integration of AWS services, Terraform infrastructure as code, and the OpenAI API with an innovative approach to automated GitHub issue creation.

## Overview

The project is structured into two main components:

1. **Discord Bot**: A Python-based bot that listens to commands and interactions within a Discord server. It's capable of responding to simple commands and is designed to be easily extendable for more complex interactions.

2. **Issue Creator Lambda Function**: An AWS Lambda function that uses the OpenAI API to generate GitHub issues based on error logs captured from the Discord bot and its code. This demonstrates an innovative approach to automated issue creation by using a large language model to interpret error logs.

## Getting Started

To get started with this project, you'll need to have the following prerequisites:

- An AWS account
- Terraform installed
- A Discord account and a server where you can add the bot
- An OpenAI API key
- A GitHub account, Personal Access Token (PAT), and a repository where you can create issues

### Setup Instructions

1. **Create a Discord Application**: Before cloning the repository, you need to create a Discord application for your bot. Go to the Discord Developer Portal, create a new application, and note down the application's public key and token. These will be used later to configure the Discord bot.

2. **Clone the Repository**: Now, clone this repository to your local machine.

   ```shell
   git clone https://github.com/autimo/demo-yvr-devops-genai.git
   ```

3. **Configure AWS Credentials**: Ensure your AWS credentials are configured properly. This can be done by setting up the AWS CLI and running `aws configure` or setting the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` environment variables.

4. **Terraform Initialization**: Navigate to the `terraform` directory and run `terraform init` to initialize the Terraform environment.

5. **Deploy Infrastructure**: Apply the Terraform configuration to deploy the necessary infrastructure to AWS.

   ```shell
   terraform apply
   ```

   Enter the required variables when prompted or create a `terraform.tfvars` file in the `terraform` directory with your specific values.

## GitHub Secrets and Variables

In order to successfully deploy and operate the components of this project, certain variables and secrets need to be configured in your GitHub repository's actions. Here's a breakdown of what's required:

### Secrets

- `DISCORD_APPLICATION_ID`: The application ID of your Discord bot. This is required for the bot to authenticate with Discord's API.
- `DISCORD_BOT_TOKEN`: The token for your Discord bot. This is used to log in the bot to Discord.
- `DISCORD_GUILD_ID`: The ID of the Discord server (guild) where the bot is added. This is necessary for registering bot commands to a specific server.
- `OPENAI_API_KEY`: Your OpenAI API key, required for the Issue Creator Lambda function to generate GitHub issues.
- `GH_PAT`: A GitHub Personal Access Token with the necessary permissions to create issues in the specified repository.

### Variables

These are configured as environment variables in the `.github/workflows/push.yaml` file and are used across different steps in the GitHub Actions workflow:

- `TF_VERSION`: The version of Terraform to use. This project uses `1.7.5`.
- `PYTHON_VERSION`: The version of Python to use for running scripts. This project uses `3.12`.

Additionally, the following variables are used within the Terraform configuration and are prompted during the `terraform apply` command, but can also be predefined in a `terraform.tfvars` file:

- `AWS_IAM_ROLE_ARN`: The ARN of the AWS IAM role that GitHub Actions will assume for deploying resources.
- `AWS_REGION`: The AWS region where resources will be deployed.
- `AWS_S3_BUCKET_NAME`: The name of the S3 bucket used by Terraform for state storage.
- `AWS_DYNAMODB_TABLE_NAME`: The name of the DynamoDB table used by Terraform for state locking.

Ensure these secrets and variables are correctly set up in your GitHub repository and AWS account for the smooth operation of the project.

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
