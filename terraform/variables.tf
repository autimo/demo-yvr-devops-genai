variable "example_lambda_git_repo_url" {
  description = "The URL of the GitHub repository containing the source code for the Example Lambda"
  type        = string
  default     = "https://github.com/autimo/aws-genai-error-reporting"
}

variable "github_access_token" {
  description = "The GitHub access token"
  type        = string
  sensitive   = true
  default     = "ghp_1234567890"
}
