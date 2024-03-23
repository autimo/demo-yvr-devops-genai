variable "discord_bot_repo_url" {
  description = "The URL of the GitHub repository containing the source code for the Discord bot"
  type        = string
  default     = "https://github.com/autimo/demo-yvr-devops-genai"
}

variable "openai_api_key" {
  description = "The OpenAI API key"
  type        = string
  sensitive   = true
  default     = "sk-YOUR_OPENAI_API_KEY"
}

variable "github_access_token" {
  description = "The GitHub access token"
  type        = string
  sensitive   = true
  default     = "ghp_1234567890"
}

variable "discord_bot_public_key" {
  description = "The public key for the Discord bot"
  type        = string
}

