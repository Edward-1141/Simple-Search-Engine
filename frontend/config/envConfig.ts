import { loadEnvConfig } from '@next/env'
 
const projectDir = process.cwd()
loadEnvConfig(projectDir)

export const envConfig = {
    BACKEND_URL: process.env.BACKEND_URL,
}