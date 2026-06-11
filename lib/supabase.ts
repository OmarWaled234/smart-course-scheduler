import AsyncStorage from "@react-native-async-storage/async-storage";
import { createClient } from "@supabase/supabase-js";

// Replace these placeholders with your Supabase project URL and anon public key.
// You can find both values in Supabase Dashboard > Project Settings > API.
const supabaseUrl = "https://YOUR_PROJECT_ID.supabase.co";
const supabaseAnonKey = "YOUR_SUPABASE_ANON_KEY";

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false
  }
});
