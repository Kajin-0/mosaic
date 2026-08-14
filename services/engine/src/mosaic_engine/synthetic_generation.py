import base64
import hashlib
from dataclasses import dataclass
from typing import Protocol

from mosaic_engine.synthetic_models import (
    SyntheticGenerationProvenance,
    SyntheticStimulusSpecification,
)

MOCK_SYNTHETIC_GENERATOR_ADAPTER_KEY = "deterministic-svg"
MOCK_SYNTHETIC_GENERATOR_ADAPTER_VERSION = "deterministic-svg-1.0.0"
MOCK_SYNTHETIC_PROVIDER = "mosaic-local-mock"
MOCK_SYNTHETIC_MODEL = "geometric-face-card"
MOCK_SYNTHETIC_MODEL_REVISION = "1.0.0"


@dataclass(frozen=True)
class GeneratedSyntheticAsset:
    media_type: str
    content_sha256: str
    asset_uri: str
    provenance: SyntheticGenerationProvenance


class SyntheticGeneratorAdapter(Protocol):
    key: str
    version: str

    def generate(self, specification: SyntheticStimulusSpecification) -> GeneratedSyntheticAsset: ...


class DeterministicSvgGenerator:
    key = MOCK_SYNTHETIC_GENERATOR_ADAPTER_KEY
    version = MOCK_SYNTHETIC_GENERATOR_ADAPTER_VERSION

    def generate(self, specification: SyntheticStimulusSpecification) -> GeneratedSyntheticAsset:
        controls = specification.control_vector
        face_width = 82 + int(controls.get("face_width", 0.5) * 46)
        eye_spacing = 28 + int(controls.get("eye_spacing", 0.5) * 30)
        smile = 8 + int(controls.get("smile", 0.5) * 20)
        contrast = 40 + int(controls.get("contrast", 0.5) * 50)
        hair_height = 22 + int(controls.get("hair_height", 0.5) * 26)

        prompt = specification.prompt_template.format(
            candidate_key=specification.candidate_key,
            seed=specification.seed,
        )
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="640" '
            'viewBox="0 0 512 640">'
            f'<rect width="512" height="640" fill="hsl({specification.seed % 360} 18% 18%)"/>'
            '<rect x="64" y="48" width="384" height="544" rx="28" fill="#f4f1ec"/>'
            f'<ellipse cx="256" cy="286" rx="{face_width}" ry="128" fill="#d7b79e"/>'
            f'<path d="M{256-face_width} 245 Q256 {150-hair_height} {256+face_width} 245 '
            f'L{256+face_width-8} 184 Q256 {118-hair_height} {256-face_width+8} 184Z" '
            f'fill="rgb({contrast},{contrast},{contrast})"/>'
            f'<circle cx="{256-eye_spacing}" cy="276" r="9" fill="#232323"/>'
            f'<circle cx="{256+eye_spacing}" cy="276" r="9" fill="#232323"/>'
            f'<path d="M220 340 Q256 {340+smile} 292 340" fill="none" '
            'stroke="#7c3f3f" stroke-width="7" stroke-linecap="round"/>'
            f'<text x="256" y="500" text-anchor="middle" font-family="sans-serif" '
            f'font-size="24" font-weight="700" fill="#222">{specification.candidate_key}</text>'
            '<text x="256" y="536" text-anchor="middle" font-family="sans-serif" '
            'font-size="17" fill="#666">Synthetic calibration candidate</text>'
            '</svg>'
        )
        raw = svg.encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        encoded = base64.b64encode(raw).decode("ascii")
        return GeneratedSyntheticAsset(
            media_type="image/svg+xml",
            content_sha256=digest,
            asset_uri=f"data:image/svg+xml;base64,{encoded}",
            provenance=SyntheticGenerationProvenance(
                adapter_key=self.key,
                adapter_version=self.version,
                provider=MOCK_SYNTHETIC_PROVIDER,
                model=MOCK_SYNTHETIC_MODEL,
                model_revision=MOCK_SYNTHETIC_MODEL_REVISION,
                seed=specification.seed,
                prompt=prompt,
                parameters={
                    key: round(value, 6)
                    for key, value in sorted(specification.control_vector.items())
                },
            ),
        )
