import React, { useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

const nodeTypes = {}; // Define outside to avoid recreation
const edgeTypes = {};

const NetworkGraph = ({ data }) => {
    // Transform data into nodes and edges
    const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
        if (!data) return { nodes: [], edges: [] };

        const nodes = [];
        const edges = [];

        // HQ Node
        nodes.push({
            id: 'hq',
            type: 'input',
            data: { label: data.name },
            position: { x: 250, y: 0 },
            style: { background: '#3b82f6', color: 'white', border: 'none', borderRadius: '8px', padding: '10px' }
        });

        // Subsidiaries
        data.subsidiaries.forEach((sub, index) => {
            const id = `sub-${index}`;
            nodes.push({
                id,
                data: { label: sub.name },
                position: { x: (index % 3) * 200, y: 150 + Math.floor(index / 3) * 100 },
                style: { background: '#1e293b', color: 'white', border: '1px solid #475569', borderRadius: '8px', padding: '8px' }
            });

            edges.push({
                id: `e-hq-${id}`,
                source: 'hq',
                target: id,
                animated: true,
                style: { stroke: '#64748b' }
            });
        });

        return { nodes, edges };
    }, [data]);

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // Update nodes when data changes (simple reset for now)
    React.useEffect(() => {
        setNodes(initialNodes);
        setEdges(initialEdges);
    }, [initialNodes, initialEdges, setNodes, setEdges]);

    return (
        <div className="h-full w-full rounded-xl overflow-hidden border border-white/10 shadow-lg bg-slate-950">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                edgeTypes={edgeTypes}
                fitView
            >
                <Background color="#475569" gap={16} />
                <Controls />
                <MiniMap nodeColor="#3b82f6" />
            </ReactFlow>
        </div>
    );
};

export default NetworkGraph;
