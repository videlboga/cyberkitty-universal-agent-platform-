import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import { Card, Button, Row, Col, Spin } from "antd";
import Link from "next/link";

interface Scenario {
  id: string;
  name: string;
  steps?: any[];
}

const ScenariosPage: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/scenarios")
      .then((res) => res.json())
      .then((data) => {
        setScenarios(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1>Сценарии</h1>
        <Link href="/scenarios/editor">
          <Button type="primary">Создать сценарий</Button>
        </Link>
      </div>
      {loading ? (
        <Spin />
      ) : (
        <Row gutter={[16, 16]}>
          {scenarios.map((scenario) => (
            <Col xs={24} sm={12} md={8} key={scenario.id}>
              <Card
                title={scenario.name || "Без названия"}
                extra={
                  <Link href={`/scenarios/editor?id=${scenario.id}`}>
                    <Button size="small">Редактировать</Button>
                  </Link>
                }
              >
                <div>Шагов: {scenario.steps?.length ?? 0}</div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Layout>
  );
};

export default ScenariosPage; 