import React, { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import AgentCard from "../../components/AgentCard";
import { Row, Col, Button, Modal, Spin, message } from "antd";

interface Agent {
  id: string;
  name: string;
  config?: Record<string, any>;
}

const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [runResult, setRunResult] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    setFetching(true);
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => setAgents(data))
      .catch(() => message.error("Ошибка загрузки агентов"))
      .finally(() => setFetching(false));
  }, []);

  const handleRun = async (agentId: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/agents/${agentId}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: { user_message: "Тестовый запуск" } }),
      });
      if (res.ok) {
        const data = await res.json();
        setRunResult(data);
        setModalOpen(true);
      } else {
        message.error("Ошибка запуска сценария");
      }
    } catch {
      message.error("Ошибка запуска сценария");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <h1 style={{ marginBottom: 24 }}>Список агентов</h1>
      {fetching ? (
        <Spin />
      ) : (
        <Row gutter={[16, 16]}>
          {agents.map((agent) => (
            <Col xs={24} sm={12} md={8} key={agent.id}>
              <AgentCard name={agent.name} config={agent.config} />
              <Button
                type="primary"
                style={{ marginTop: 8 }}
                onClick={() => handleRun(agent.id)}
                loading={loading}
                block
              >
                Запустить
              </Button>
            </Col>
          ))}
        </Row>
      )}
      <Modal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
        title="Результат запуска"
      >
        {runResult ? (
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(runResult, null, 2)}</pre>
        ) : (
          <Spin />
        )}
      </Modal>
    </Layout>
  );
};

export default AgentsPage; 