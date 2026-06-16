import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://lqihpzzxssgutmcdmusy.supabase.co'
const SUPABASE_ANON_KEY = 'sb_publishable_QZ5Tg-n4QPCB2H2g39qNRA_9IykLqd0'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
