import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://lqihpzzxssgutmcdmusy.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxxaWhwenp4c3NndXRtY2RtdXN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2MDk1MDcsImV4cCI6MjA5NzE4NTUwN30.E4WKYvkatmE86ICucCis8pMIjF4IjTRFWOYsuxEbXcI'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
