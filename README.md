# ComfyUI-SAM3-JSON-Boxes-API v2

Supports these JSON formats:

```json
{ "regions": [{ "x1": 78, "y1": 0, "x2": 312, "y2": 119 }] }
```

```json
{ "regions": [{ "x1": 78, "y1": 0, "width": 234, "height": 119 }] }
```

```json
{ "regions": [{ "x": 78, "y": 0, "w": 234, "h": 119 }] }
```

```json
{ "regions": [{ "x": 78, "y": 0, "width": 234, "height": 119 }] }
```

The node converts everything into normalized SAM3 box format: center_x, center_y, width, height.

Install folder should be renamed/placed as:

```text
ComfyUI/custom_nodes/ComfyUI-SAM3-JSON-Boxes-API
```

Search node:

```text
JSON Regions to SAM3 Boxes API
```
