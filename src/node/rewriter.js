import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from project root
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

/**
 * AI Content Rewriter
 * Reads transcript from stdin, calls OpenAI API, and outputs JSON to stdout.
 */

async function main() {
  // 1. Read input transcript from stdin
  let transcript = '';
  if (!process.stdin.isTTY) {
    for await (const chunk of process.stdin) {
      transcript += chunk;
    }
  }

  if (!transcript || transcript.trim().length < 10) {
    // If no stdin or too short, check if it's a test run
    if (process.argv.includes('--test')) {
      transcript = "这是一段测试转录文本，内容关于人工智能的未来。";
    } else {
      console.error("[错误] 未接收到有效的转录文本");
      process.exit(1);
    }
  }

  // 2. Load configuration
  const configPath = path.join(__dirname, '../../config/sources.yaml');
  let promptPath = path.join(__dirname, '../../config/rewrite-prompt.md');

  // Check for custom prompt path from args
  const promptArgIndex = process.argv.indexOf('--prompt');
  if (promptArgIndex !== -1 && process.argv[promptArgIndex + 1]) {
    promptPath = process.argv[promptArgIndex + 1];
  }

  let config;
  try {
    const configContent = fs.readFileSync(configPath, 'utf8');
    config = yaml.load(configContent);
  } catch (error) {
    console.error(`[错误] 无法加载配置文件: ${error.message}`);
    process.exit(1);
  }

  const openaiConfig = config.api?.openai || {};

  // 3. Load System Prompt
  let systemPrompt = '';
  try {
    systemPrompt = fs.readFileSync(promptPath, 'utf8');
  } catch (error) {
    console.error(`[错误] 无法加载提示词文件: ${error.message}`);
    process.exit(1);
  }

  // 4. Call AI (OpenAI compatible)
  const apiKey = process.env.OPENAI_API_KEY || openaiConfig.api_key;
  const baseURL = process.env.OPENAI_BASE_URL || openaiConfig.base_url;
  const model = process.env.OPENAI_MODEL || openaiConfig.model || 'gpt-4o';

  if (!apiKey || apiKey.includes('your_api_key') || apiKey.trim() === '') {
    console.error("[错误] 未配置有效的 OpenAI API Key (.env 或 config.yaml)");
    process.exit(1);
  }

  const client = new OpenAI({
    apiKey: apiKey,
    baseURL: baseURL || 'https://api.openai.com/v1',
  });

  try {
    const response = await client.chat.completions.create({
      model: model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: `以下是需要改写的转录文本：\n\n${transcript}` }
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
    });

    const result = response.choices[0].message.content;

    // Output directly to stdout as it will be captured by Python
    process.stdout.write(result);
  } catch (error) {
    console.error(`[错误] AI 调用失败: ${error.message}`);
    process.exit(1);
  }
}

main().catch(error => {
  console.error(`[未捕获故障] ${error.stack}`);
  process.exit(1);
});
