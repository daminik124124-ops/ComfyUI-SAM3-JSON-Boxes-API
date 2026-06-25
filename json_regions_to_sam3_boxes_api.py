import json


class JSONRegionsToSAM3BoxesAPI:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "json_text": ("STRING", {
                    "multiline": True,
                    "default": '{\n  "regions": [\n    { "x1": 78, "y1": 0, "width": 234, "height": 119 }\n  ]\n}'
                }),
                "padding": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
            }
        }

    RETURN_TYPES = ("SAM3_BOXES_PROMPT", "SAM3_BOXES_PROMPT", "STRING")
    RETURN_NAMES = ("positive_boxes", "negative_boxes", "debug_info")
    FUNCTION = "run"
    CATEGORY = "SAM3/prompts"

    def _extract_regions(self, data):
        if isinstance(data, list):
            return data, []
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object or a list of region objects.")

        positive = (
            data.get("positive_regions")
            or data.get("regions")
            or data.get("boxes")
            or data.get("positive_boxes")
            or []
        )
        negative = data.get("negative_regions") or data.get("negative_boxes") or []
        return positive, negative

    def _region_to_xyxy(self, r, idx):
        if isinstance(r, dict):
            if all(k in r for k in ("x1", "y1", "x2", "y2")):
                return float(r["x1"]), float(r["y1"]), float(r["x2"]), float(r["y2"])

            if all(k in r for k in ("x1", "y1", "width", "height")):
                x1 = float(r["x1"])
                y1 = float(r["y1"])
                return x1, y1, x1 + float(r["width"]), y1 + float(r["height"])

            if all(k in r for k in ("x", "y", "w", "h")):
                x1 = float(r["x"])
                y1 = float(r["y"])
                return x1, y1, x1 + float(r["w"]), y1 + float(r["h"])

            if all(k in r for k in ("x", "y", "width", "height")):
                x1 = float(r["x"])
                y1 = float(r["y"])
                return x1, y1, x1 + float(r["width"]), y1 + float(r["height"])

            raise ValueError(
                f"Bad region at index {idx}: {r}. "
                "Supported: x1/y1/x2/y2, x1/y1/width/height, x/y/w/h, x/y/width/height."
            )

        if isinstance(r, (list, tuple)) and len(r) >= 4:
            return tuple(map(float, r[:4]))

        raise ValueError(f"Bad region at index {idx}: {r}")

    def _to_prompt(self, regions, label, img_w, img_h, padding):
        boxes = []
        labels = []

        for idx, r in enumerate(regions):
            x1, y1, x2, y2 = self._region_to_xyxy(r, idx)

            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1

            x1 = max(0.0, x1 - padding)
            y1 = max(0.0, y1 - padding)
            x2 = min(float(img_w), x2 + padding)
            y2 = min(float(img_h), y2 + padding)

            if x2 <= x1 or y2 <= y1:
                continue

            x1n = x1 / img_w
            y1n = y1 / img_h
            x2n = x2 / img_w
            y2n = y2 / img_h

            cx = (x1n + x2n) / 2.0
            cy = (y1n + y2n) / 2.0
            w = x2n - x1n
            h = y2n - y1n

            boxes.append([cx, cy, w, h])
            labels.append(bool(label))

        return {"boxes": boxes, "labels": labels}

    def run(self, image, json_text, padding=0):
        img_h = int(image.shape[1])
        img_w = int(image.shape[2])

        if not str(json_text).strip():
            raise ValueError("json_text is empty.")

        data = json.loads(json_text)
        positive_regions, negative_regions = self._extract_regions(data)

        positive_prompt = self._to_prompt(positive_regions, True, img_w, img_h, padding)
        negative_prompt = self._to_prompt(negative_regions, False, img_w, img_h, padding)

        debug = (
            f"Mode: API/json_text\n"
            f"Image: {img_w}x{img_h}\n"
            f"Positive regions: {len(positive_regions)} -> boxes: {len(positive_prompt['boxes'])}\n"
            f"Negative regions: {len(negative_regions)} -> boxes: {len(negative_prompt['boxes'])}\n"
            f"Padding: {padding}px\n"
            f"Supported input: x1/y1/x2/y2, x1/y1/width/height, x/y/w/h"
        )

        return (positive_prompt, negative_prompt, debug)


NODE_CLASS_MAPPINGS = {
    "JSONRegionsToSAM3BoxesAPI": JSONRegionsToSAM3BoxesAPI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JSONRegionsToSAM3BoxesAPI": "JSON Regions to SAM3 Boxes API",
}
