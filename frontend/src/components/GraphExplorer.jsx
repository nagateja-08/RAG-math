import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, ZoomIn, ZoomOut, RefreshCw, Layers, BookOpen, 
  CheckCircle2, ArrowRight, X, ExternalLink, HelpCircle, Sparkles 
} from 'lucide-react';
import { fetchGraph, fetchConceptDetails } from '../services/api';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

const TYPE_COLORS = {
  Concept: '#3b82f6',     // Blue
  Formula: '#10b981',     // Green
  Theorem: '#8b5cf6',     // Purple
  Topic: '#f59e0b',       // Amber
  Subtopic: '#f97316',    // Orange
  Example: '#ec4899',     // Pink
};

const SUBJECT_FILTERS = ['All', 'Calculus', 'Algebra', 'Trigonometry', 'Probability', 'Statistics'];

export default function GraphExplorer({ onSelectConceptForChat, onStartQuiz }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodeDetails, setNodeDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const transformRef = useRef({ x: 0, y: 0, scale: 0.85 });
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const draggedNodeRef = useRef(null);
  const physicsNodesRef = useRef([]);

  // Load Graph Data
  useEffect(() => {
    loadGraphData(selectedSubject);
  }, [selectedSubject]);

  const loadGraphData = async (subject) => {
    setLoading(true);
    try {
      const data = await fetchGraph(subject);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      initPhysics(data.nodes || [], data.edges || []);
    } catch (err) {
      console.error('Failed to load graph:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initialize Force Simulation coordinates
  const initPhysics = (rawNodes, rawEdges) => {
    const width = 1000;
    const height = 650;
    const count = rawNodes.length;

    // Arrange in circular topic clusters
    const clusters = {
      Calculus: { cx: -250, cy: -150 },
      Algebra: { cx: 250, cy: -150 },
      Trigonometry: { cx: -250, cy: 180 },
      Probability: { cx: 250, cy: 180 },
      Statistics: { cx: 0, cy: 300 },
      General: { cx: 0, cy: 0 },
    };

    const pNodes = rawNodes.map((n, i) => {
      const cluster = clusters[n.subject] || clusters.General;
      const angle = (i / count) * 2 * Math.PI;
      const radius = 60 + Math.random() * 120;
      return {
        ...n,
        x: cluster.cx + Math.cos(angle) * radius,
        y: cluster.cy + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: n.type === 'Topic' ? 24 : n.type === 'Theorem' ? 18 : 16,
      };
    });

    physicsNodesRef.current = pNodes;
  };

  // Canvas Render Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let running = true;

    const render = () => {
      if (!running) return;

      const width = canvas.parentElement.clientWidth;
      const height = canvas.parentElement.clientHeight;
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }

      ctx.clearRect(0, 0, width, height);
      ctx.save();

      // Pan & Zoom
      ctx.translate(width / 2 + transformRef.current.x, height / 2 + transformRef.current.y);
      ctx.scale(transformRef.current.scale, transformRef.current.scale);

      const pNodes = physicsNodesRef.current;
      const nodeMap = new Map(pNodes.map((n) => [n.id, n]));

      // 1. Draw Edges
      edges.forEach((edge) => {
        const u = nodeMap.get(edge.source);
        const v = nodeMap.get(edge.target);
        if (!u || !v) return;

        const isHighlighted =
          selectedNode && (selectedNode.id === edge.source || selectedNode.id === edge.target);

        ctx.beginPath();
        ctx.moveTo(u.x, u.y);
        ctx.lineTo(v.x, v.y);

        if (edge.type === 'PREREQUISITE_OF') {
          ctx.strokeStyle = isHighlighted ? '#3b82f6' : 'rgba(147, 197, 253, 0.45)';
          ctx.lineWidth = isHighlighted ? 2.5 : 1.5;
          ctx.setLineDash([]);
        } else if (edge.type === 'USES_FORMULA') {
          ctx.strokeStyle = isHighlighted ? '#10b981' : 'rgba(52, 211, 153, 0.45)';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
        } else if (edge.type === 'PROVES' || edge.type === 'EXPLAINS') {
          ctx.strokeStyle = isHighlighted ? '#8b5cf6' : 'rgba(196, 181, 253, 0.45)';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([2, 2]);
        } else {
          ctx.strokeStyle = 'rgba(156, 163, 175, 0.25)';
          ctx.lineWidth = 1;
          ctx.setLineDash([1, 3]);
        }
        ctx.stroke();
        ctx.setLineDash([]);
      });

      // 2. Draw Nodes
      pNodes.forEach((node) => {
        const isSelected = selectedNode && selectedNode.id === node.id;
        const isMatch =
          searchQuery &&
          node.name.toLowerCase().includes(searchQuery.toLowerCase());

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + (isSelected ? 4 : 0), 0, 2 * Math.PI);

        // Fill color
        ctx.fillStyle = TYPE_COLORS[node.type] || '#6b7280';
        ctx.fill();

        // Stroke
        ctx.lineWidth = isSelected ? 3 : isMatch ? 2.5 : 1.5;
        ctx.strokeStyle = isSelected ? '#ffffff' : isMatch ? '#fbbf24' : 'rgba(255, 255, 255, 0.7)';
        ctx.stroke();

        // Node Label
        ctx.font = isSelected ? 'bold 12px sans-serif' : '11px sans-serif';
        ctx.fillStyle = isSelected ? '#38bdf8' : '#e2e8f0';
        ctx.textAlign = 'center';
        ctx.fillText(node.name, node.x, node.y + node.radius + 14);
      });

      ctx.restore();
      animFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      running = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [edges, selectedNode, searchQuery]);

  // Click & Drag Handlers
  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left - canvasRef.current.width / 2 - transformRef.current.x;
    const clickY = e.clientY - rect.top - canvasRef.current.height / 2 - transformRef.current.y;
    const s = transformRef.current.scale;
    const graphX = clickX / s;
    const graphY = clickY / s;

    // Check if clicked a node
    const clicked = physicsNodesRef.current.find((n) => {
      const dx = n.x - graphX;
      const dy = n.y - graphY;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 5;
    });

    if (clicked) {
      draggedNodeRef.current = clicked;
      setSelectedNode(clicked);
      inspectNode(clicked.name);
    } else {
      isDraggingRef.current = true;
      dragStartRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseMove = (e) => {
    if (draggedNodeRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const s = transformRef.current.scale;
      draggedNodeRef.current.x =
        (e.clientX - rect.left - canvasRef.current.width / 2 - transformRef.current.x) / s;
      draggedNodeRef.current.y =
        (e.clientY - rect.top - canvasRef.current.height / 2 - transformRef.current.y) / s;
    } else if (isDraggingRef.current) {
      const dx = e.clientX - dragStartRef.current.x;
      const dy = e.clientY - dragStartRef.current.y;
      transformRef.current.x += dx;
      transformRef.current.y += dy;
      dragStartRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseUp = () => {
    draggedNodeRef.current = null;
    isDraggingRef.current = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    transformRef.current.scale = Math.min(2.5, Math.max(0.3, transformRef.current.scale * zoomFactor));
  };

  const zoomIn = () => {
    transformRef.current.scale = Math.min(2.5, transformRef.current.scale * 1.2);
  };

  const zoomOut = () => {
    transformRef.current.scale = Math.max(0.3, transformRef.current.scale * 0.8);
  };

  const resetView = () => {
    transformRef.current = { x: 0, y: 0, scale: 0.85 };
  };

  const inspectNode = async (name) => {
    setDetailsLoading(true);
    try {
      const details = await fetchConceptDetails(name);
      setNodeDetails(details);
    } catch (err) {
      console.error('Failed to load concept details:', err);
    } finally {
      setDetailsLoading(false);
    }
  };

  return (
    <div className="relative w-full h-[650px] bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
      {/* Top Toolbar */}
      <div className="p-4 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 z-10">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-slate-100 text-sm md:text-base">
            Mathematical Knowledge Graph Explorer
          </h2>
          <span className="text-xs bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded-full border border-indigo-500/20 font-medium">
            {nodes.length} Nodes &bull; {edges.length} Edges
          </span>
        </div>

        {/* Subject Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1">
          {SUBJECT_FILTERS.map((subj) => (
            <button
              key={subj}
              onClick={() => setSelectedSubject(subj)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                selectedSubject === subj
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {subj}
            </button>
          ))}
        </div>

        {/* Search & Zoom Controls */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search concepts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500 w-36 md:w-48"
            />
          </div>
          <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700 p-0.5">
            <button onClick={zoomIn} className="p-1 hover:text-white text-slate-400" title="Zoom In">
              <ZoomIn className="w-4 h-4" />
            </button>
            <button onClick={zoomOut} className="p-1 hover:text-white text-slate-400" title="Zoom Out">
              <ZoomOut className="w-4 h-4" />
            </button>
            <button onClick={resetView} className="p-1 hover:text-white text-slate-400" title="Reset View">
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Interactive Canvas */}
      <div className="relative flex-1 w-full h-full cursor-grab active:cursor-grabbing">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 z-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500" />
          </div>
        )}

        <canvas
          ref={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onWheel={handleWheel}
          className="w-full h-full block"
        />

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-xl p-3 flex flex-wrap gap-3 text-xs text-slate-300 pointer-events-none">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-blue-500" /> Concept
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-500" /> Formula
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-purple-500" /> Theorem
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-amber-500" /> Topic
          </div>
        </div>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-84 md:w-96 max-h-[90%] bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl p-5 overflow-y-auto z-30 transition-all text-slate-200">
            <div className="flex items-start justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <span
                  className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider"
                  style={{
                    backgroundColor: `${TYPE_COLORS[selectedNode.type]}20`,
                    color: TYPE_COLORS[selectedNode.type],
                    border: `1px solid ${TYPE_COLORS[selectedNode.type]}40`,
                  }}
                >
                  {selectedNode.type} &bull; {selectedNode.subject}
                </span>
                <h3 className="text-lg font-bold text-white mt-1">{selectedNode.name}</h3>
                <span className="text-xs text-slate-400">Difficulty: {selectedNode.difficulty}</span>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Description */}
            <div className="mt-3 text-xs text-slate-300 leading-relaxed">
              {selectedNode.description || 'Mathematical concept node within curriculum knowledge graph.'}
            </div>

            {/* LaTeX if available */}
            {selectedNode.latex && (
              <div className="mt-3 p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-center">
                <BlockMath math={selectedNode.latex} />
              </div>
            )}

            {/* Neighborhood Details */}
            {detailsLoading ? (
              <div className="py-6 flex justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-400" />
              </div>
            ) : nodeDetails ? (
              <div className="mt-4 space-y-3">
                {/* Prerequisites */}
                {nodeDetails.prerequisites && nodeDetails.prerequisites.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5 text-blue-400" /> Prerequisites
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {nodeDetails.prerequisites.map((p, idx) => (
                        <span
                          key={idx}
                          onClick={() => inspectNode(p)}
                          className="text-xs bg-blue-500/10 text-blue-300 border border-blue-500/20 px-2 py-1 rounded-md cursor-pointer hover:bg-blue-500/20"
                        >
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Formulas */}
                {nodeDetails.formulas && nodeDetails.formulas.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Governing Formulas
                    </h4>
                    <div className="space-y-1.5">
                      {nodeDetails.formulas.map((f, idx) => (
                        <div key={idx} className="p-2 bg-slate-950/60 border border-slate-800 rounded-lg text-xs">
                          <div className="font-medium text-emerald-300">{f.name}</div>
                          {f.latex && <InlineMath math={f.latex} />}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Theorems */}
                {nodeDetails.theorems && nodeDetails.theorems.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" /> Connected Theorems
                    </h4>
                    <div className="space-y-1.5">
                      {nodeDetails.theorems.map((t, idx) => (
                        <div key={idx} className="p-2 bg-slate-950/60 border border-slate-800 rounded-lg text-xs text-purple-200">
                          <div className="font-medium">{t.name}</div>
                          <div className="text-[11px] text-slate-400 mt-0.5">{t.statement}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}

            {/* Action Buttons */}
            <div className="mt-5 pt-3 border-t border-slate-800 flex flex-col gap-2">
              <button
                onClick={() => {
                  if (onSelectConceptForChat) onSelectConceptForChat(selectedNode.name);
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all shadow-lg shadow-indigo-600/20"
              >
                <span>Ask MathGPT about {selectedNode.name}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => {
                  if (onStartQuiz) onStartQuiz(selectedNode.name);
                }}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold border border-slate-700 transition-all"
              >
                <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Test Readiness & Prerequisites</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
