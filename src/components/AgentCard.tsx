import React from "react";
import { Card, Tag } from "antd";

interface AgentCardProps {
  name: string;
  config?: Record<string, any>;
}

const AgentCard: React.FC<AgentCardProps> = ({ name, config }) => (
  <Card title={name} style={{ marginBottom: 16 }}>
    <div>
      <b>Роль:</b> {config?.role || "—"}
    </div>
    {config?.scenario_id && (
      <div>
        <Tag color="blue">scenario_id: {config.scenario_id}</Tag>
      </div>
    )}
  </Card>
);

export default AgentCard; 