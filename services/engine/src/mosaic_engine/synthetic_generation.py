import base64
import binascii
import hashlib
import struct
import zlib
from dataclasses import dataclass
from typing import Protocol

from mosaic_engine.synthetic_models import (
    SyntheticGenerationProvenance,
    SyntheticStimulusSpecification,
)

MOCK_SYNTHETIC_GENERATOR_ADAPTER_KEY = "deterministic-png"
MOCK_SYNTHETIC_GENERATOR_ADAPTER_VERSION = "deterministic-png-1.0.0"
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

    def generate(
        self,
        specification: SyntheticStimulusSpecification,
    ) -> GeneratedSyntheticAsset: ...


class DeterministicPngGenerator:
    key = MOCK_SYNTHETIC_GENERATOR_ADAPTER_KEY
    version = MOCK_SYNTHETIC_GENERATOR_ADAPTER_VERSION

    def generate(self, specification: SyntheticStimulusSpecification) -> GeneratedSyntheticAsset:
        prompt = specification.prompt_template.format(
            candidate_key=specification.candidate_key,
            seed=specification.seed,
        )
        raw = self._png(specification)
        digest = hashlib.sha256(raw).hexdigest()
        encoded = base64.b64encode(raw).decode("ascii")
        return GeneratedSyntheticAsset(
            media_type="image/png",
            content_sha256=digest,
            asset_uri=f"data:image/png;base64,{encoded}",
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

    def _png(self, specification: SyntheticStimulusSpecification) -> bytes:
        width = 180
        height = 220
        controls = specification.control_vector
        face_rx = 38 + int(controls.get("face_width", 0.5) * 16)
        eye_spacing = 13 + int(controls.get("eye_spacing", 0.5) * 14)
        smile_depth = 3 + int(controls.get("smile", 0.5) * 8)
        contrast = 24 + int(controls.get("contrast", 0.5) * 62)
        hair_height = 18 + int(controls.get("hair_height", 0.5) * 18)

        hue = specification.seed % 97
        background = (28 + hue // 4, 34 + hue // 5, 42 + hue // 6, 255)
        card = (241, 238, 232, 255)
        skin = (213, 181, 156, 255)
        hair = (contrast, contrast, contrast, 255)
        ink = (35, 35, 35, 255)
        mouth = (126, 63, 63, 255)

        rows: list[bytes] = []
        cx = width // 2
        cy = 103
        face_ry = 54
        for y in range(height):
            row = bytearray([0])
            for x in range(width):
                pixel = background
                if 18 <= x < width - 18 and 12 <= y < height - 12:
                    pixel = card

                face_equation = ((x - cx) ** 2) / (face_rx**2) + ((y - cy) ** 2) / (
                    face_ry**2
                )
                if face_equation <= 1:
                    pixel = skin

                hair_boundary = cy - face_ry + hair_height
                if face_equation <= 1 and y <= hair_boundary:
                    pixel = hair

                left_eye_x = cx - eye_spacing
                right_eye_x = cx + eye_spacing
                if (x - left_eye_x) ** 2 + (y - 100) ** 2 <= 16:
                    pixel = ink
                if (x - right_eye_x) ** 2 + (y - 100) ** 2 <= 16:
                    pixel = ink

                mouth_y = 127 + int(smile_depth * ((x - cx) ** 2) / 700)
                if cx - 22 <= x <= cx + 22 and abs(y - mouth_y) <= 1:
                    pixel = mouth

                row.extend(pixel)
            rows.append(bytes(row))

        image_data = zlib.compress(b"".join(rows), level=9)
        signature = b"\x89PNG\r\n\x1a\n"
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
        chunks = (
            self._chunk(b"IHDR", ihdr),
            self._chunk(b"IDAT", image_data),
            self._chunk(b"IEND", b""),
        )
        return signature + b"".join(chunks)

    def _chunk(self, kind: bytes, payload: bytes) -> bytes:
        checksum = binascii.crc32(kind + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", checksum)
