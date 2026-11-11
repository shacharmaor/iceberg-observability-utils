import { Alert, Badge, Container, Group, Loader, Table, Text, Title } from "@mantine/core";
import { useEffect, useState } from "react";
import { fetchOverview, Severity, TableOverview } from "./api";

const SEVERITY_COLOR: Record<Severity, string> = { critical: "red", warn: "yellow" };

export function Overview() {
  const [tables, setTables] = useState<TableOverview[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverview().then(setTables, (e: Error) => setError(e.message));
  }, []);

  return (
    <Container size="lg" py="xl">
      <Title order={2} mb="md">
        Overview
      </Title>
      {error && <Alert color="red" title="Could not load the Overview">{error}</Alert>}
      {!error && tables === null && <Loader />}
      {tables && (
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Namespace</Table.Th>
              <Table.Th>Table</Table.Th>
              <Table.Th>Findings</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {tables.map((t) => (
              <Table.Tr key={`${t.namespace}.${t.table}`}>
                <Table.Td>{t.namespace}</Table.Td>
                <Table.Td>{t.table}</Table.Td>
                <Table.Td>
                  {t.findings.length === 0 ? (
                    <Text c="dimmed">none</Text>
                  ) : (
                    <Group gap="xs">
                      {t.findings.map((f) => (
                        <Badge key={f.signal} color={SEVERITY_COLOR[f.severity]}>
                          {f.signal}: {f.value} (&gt; {f.threshold})
                        </Badge>
                      ))}
                    </Group>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Container>
  );
}
