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

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
