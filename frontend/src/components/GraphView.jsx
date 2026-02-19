import React, { useState, useEffect, useRef } from 'react'
import * as d3 from 'd3'
import '../styles/GraphView.css'

const GraphView = ({ data, onAccountClick }) => {
  const containerRef = useRef(null)
  const svgRef = useRef(null)
  const gRef = useRef(null)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 })

  const scroll = (direction, distance = 50) => {
    if (!gRef.current) return

    const g = d3.select(gRef.current)
    const currentTransform = d3.zoomTransform(d3.select(svgRef.current).node())

    let newTransform = currentTransform
    switch (direction) {
      case 'up':
        newTransform = currentTransform.translate(0, distance)
        break
      case 'down':
        newTransform = currentTransform.translate(0, -distance)
        break
      case 'left':
        newTransform = currentTransform.translate(distance, 0)
        break
      case 'right':
        newTransform = currentTransform.translate(-distance, 0)
        break
      default:
        break
    }

    d3.select(svgRef.current)
      .transition()
      .duration(300)
      .call(
        d3.zoom().transform,
        newTransform
      )
  }

  const resetView = () => {
    if (!svgRef.current) return
    d3.select(svgRef.current)
      .transition()
      .duration(500)
      .call(d3.zoom().transform, d3.zoomIdentity)
  }

  useEffect(() => {
    if (!data || !containerRef.current) return

    // Prepare graph data from rings and account scores
    const nodes = []
    const links = []
    const nodeSet = new Set()

    // Add ALL accounts as nodes from account_scores
    if (data.account_scores && data.account_scores.length > 0) {
      data.account_scores.forEach((scoreData) => {
        if (!nodeSet.has(scoreData.account_id)) {
          nodes.push({
            id: scoreData.account_id,
            group: scoreData.risk_level || 'LOW',
            score: scoreData.final_score || 0,
          })
          nodeSet.add(scoreData.account_id)
        }
      })
    }

    // Extract links from rings
    if (data.rings_detected && data.rings_detected.length > 0) {
      data.rings_detected.forEach((ring) => {
        // Create links for the ring
        for (let i = 0; i < ring.accounts.length; i++) {
          const source = ring.accounts[i]
          const target = ring.accounts[(i + 1) % ring.accounts.length]
          links.push({
            source,
            target,
            value: ring.total_amount,
            ringId: ring.ring_id,
          })
        }
      })
    }

    if (nodes.length === 0) {
      // Show message if no graph data
      d3.select(svgRef.current).selectAll('*').remove()
      d3.select(svgRef.current)
        .append('text')
        .attr('x', '50%')
        .attr('y', '50%')
        .attr('text-anchor', 'middle')
        .style('fill', '#999')
        .text('No transactions or patterns detected')
      return
    }

    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    // Clear previous SVG
    d3.select(svgRef.current).selectAll('*').remove()

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    // Create main group for zoom/pan
    const g = svg.append('g').attr('class', 'graph-group')
    gRef.current = g.node()

    // Create force simulation with optimized parameters
    const simulation = d3
      .forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(50))

    // Create links
    const link = g
      .append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d) => Math.sqrt(Math.min(d.value / 100000, 5)))

    // Create nodes
    const node = g
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d) => {
        switch (d.group) {
          case 'CRITICAL':
            return 30
          case 'HIGH':
            return 24
          case 'MEDIUM':
            return 18
          case 'LOW':
            return 12
          default:
            return 15
        }
      })
      .attr('fill', (d) => {
        switch (d.group) {
          case 'CRITICAL':
            return '#d32f2f'
          case 'HIGH':
            return '#f57c00'
          case 'MEDIUM':
            return '#fbc02d'
          case 'LOW':
            return '#388e3c'
          default:
            return '#1976d2'
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation()
        onAccountClick?.(d.id)
      })
      .on('mouseenter', function (event, d) {
        d3.select(this).transition().duration(200).attr('r', (d) => {
          switch (d.group) {
            case 'CRITICAL':
              return 38
            case 'HIGH':
              return 30
            case 'MEDIUM':
              return 22
            case 'LOW':
              return 16
            default:
              return 20
          }
        })
        
        // Show tooltip with account details
        setHoveredNode(d)
        const rect = svgRef.current.getBoundingClientRect()
        setTooltipPos({
          x: event.clientX - rect.left + 10,
          y: event.clientY - rect.top + 10,
        })
      })
      .on('mouseleave', function () {
        d3.select(this).transition().duration(200).attr('r', (d) => {
          switch (d.group) {
            case 'CRITICAL':
              return 30
            case 'HIGH':
              return 24
            case 'MEDIUM':
              return 18
            case 'LOW':
              return 12
            default:
              return 15
          }
        })
        
        // Hide tooltip
        setHoveredNode(null)
      })

    // Create labels
    const labels = g
      .append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('font-size', '12px')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .text((d) => d.id.substring(0, 8))
      .style('pointer-events', 'none')
      .style('fill', '#fff')
      .style('font-weight', 'bold')

    // Add legend to SVG (outside of zoom group)
    const legend = svg
      .append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width - 180}, 20)`)

    const riskLevels = [
      { level: 'CRITICAL', color: '#d32f2f' },
      { level: 'HIGH', color: '#f57c00' },
      { level: 'MEDIUM', color: '#fbc02d' },
      { level: 'LOW', color: '#388e3c' },
    ]

    riskLevels.forEach((risk, i) => {
      const item = legend.append('g').attr('transform', `translate(0, ${i * 25})`)

      item
        .append('circle')
        .attr('r', 6)
        .attr('fill', risk.color)

      item
        .append('text')
        .attr('x', 15)
        .attr('dy', '0.3em')
        .style('font-size', '12px')
        .text(risk.level)
    })

    // Add zoom functionality
    const zoom = d3
      .zoom()
      .scaleExtent([0.5, 8])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y)

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y)

      labels.attr('x', (d) => d.x).attr('y', (d) => d.y)
    })
  }, [data, onAccountClick])

  return (
    <div className="graph-view-container" ref={containerRef}>
      <svg ref={svgRef} className="graph-svg"></svg>

      {/* Scroll Controls */}
      <div className="graph-controls">
        {/* Up Button */}
        <button
          className="scroll-btn scroll-btn-up"
          onClick={() => scroll('up')}
          title="Scroll Up"
        >
          ▲
        </button>

        {/* Left, Center, Right Buttons */}
        <div className="scroll-btn-row">
          <button
            className="scroll-btn scroll-btn-left"
            onClick={() => scroll('left')}
            title="Scroll Left"
          >
            ◄
          </button>
          <button
            className="scroll-btn scroll-btn-reset"
            onClick={resetView}
            title="Reset View"
          >
            ⊙
          </button>
          <button
            className="scroll-btn scroll-btn-right"
            onClick={() => scroll('right')}
            title="Scroll Right"
          >
            ►
          </button>
        </div>

        {/* Down Button */}
        <button
          className="scroll-btn scroll-btn-down"
          onClick={() => scroll('down')}
          title="Scroll Down"
        >
          ▼
        </button>
      </div>

      {/* Tooltip for account details on hover */}
      {hoveredNode && (
        <div
          className="account-tooltip"
          style={{
            left: `${tooltipPos.x}px`,
            top: `${tooltipPos.y}px`,
          }}
        >
          <div className="tooltip-header">
            <div className={`risk-badge risk-${hoveredNode.group.toLowerCase()}`}>
              {hoveredNode.group}
            </div>
            <div className="account-id">{hoveredNode.id}</div>
          </div>
          <div className="tooltip-body">
            <div className="tooltip-row">
              <span className="tooltip-label">Risk Score:</span>
              <span className="tooltip-value">{hoveredNode.score.toFixed(1)}/100</span>
            </div>
            <div className="tooltip-row">
              <span className="tooltip-label">Risk Level:</span>
              <span className="tooltip-value">{hoveredNode.group}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default GraphView
