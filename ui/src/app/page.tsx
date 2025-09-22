import { Suspense } from "react";
import { StartupEvalContainer } from "@/components/StartupEvalContainer";

export default function HomePage(): React.JSX.Element {
  return (
    <div className="flex flex-col h-screen">
      <Suspense fallback={<div>Loading...</div>}>
        <StartupEvalContainer />
      </Suspense>
    </div>
  );
}