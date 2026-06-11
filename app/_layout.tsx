import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          contentStyle: { backgroundColor: "#f8fafc" },
          headerShadowVisible: false,
          headerStyle: { backgroundColor: "#f8fafc" },
          headerTitleStyle: { color: "#0f172a", fontWeight: "800" }
        }}
      />
    </>
  );
}
