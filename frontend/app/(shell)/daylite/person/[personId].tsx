import React from "react";
import { useLocalSearchParams } from "expo-router";
import { PageContainer } from "@/components/layout/PageContainer";
import { PersonDetailView } from "@/features/modules/person/PersonDetailView";
import { ErrorState } from "@/components/ui/ErrorState";

/**
 * Dedicated Full-Page Person Detail Route
 * Path: /daylite/person/[personId]
 * Loads complete 8-table profile for a specific PersonID with deep-linking & refresh support.
 */
export default function DaylitePersonDetailScreen() {
  const { personId } = useLocalSearchParams<{ personId: string }>();
  const parsedId = personId ? parseInt(personId, 10) : NaN;

  if (isNaN(parsedId)) {
    return (
      <PageContainer>
        <ErrorState
          title="Invalid Person ID"
          message={`The provided Person ID "${personId}" is not a valid numerical identifier.`}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer scrollable={true}>
      <PersonDetailView personId={parsedId} />
    </PageContainer>
  );
}
