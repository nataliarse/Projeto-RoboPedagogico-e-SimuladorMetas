from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from trt18_collector import collector_trt18, service
from trt18_collector.models import Coleta, DadosProcesso, Processo, StatusColeta
from trt18_collector.normalizer import normalizar


VALID_NUMBER = "00110008219815180051"


def _cnj(*, segment: str = "5", tribunal: str = "18") -> str:
    base = f"0000001002026{segment}{tribunal}0001"
    dv = collector_trt18.digito_verificador_cnj(base)
    return f"{base[:7]}{dv:02d}{base[9:]}"


class _CachePath:
    def __init__(self, target: Path) -> None:
        self.target = target

    def __truediv__(self, _name: str) -> Path:
        return self.target


@pytest.fixture
def cache_file():
    path = Path(__file__).parent / f".p6-cache-{uuid4().hex}.json"
    yield path
    path.unlink(missing_ok=True)


@pytest.mark.parametrize(
    ("number", "message"),
    [
        ("123", "20"),
        (VALID_NUMBER[:7] + "00" + VALID_NUMBER[9:], "verificador"),
        (_cnj(segment="8"), "segmento"),
        (_cnj(tribunal="10"), "TRT10"),
    ],
)
def test_cnj_rejects_invalid_contract_variants(number, message):
    with pytest.raises(ValueError, match=message):
        collector_trt18.validar_numero_cnj(number)


def test_cnj_accepts_formatted_trt18_number():
    assert collector_trt18.validar_numero_cnj("0011000-82.1981.5.18.0051") == VALID_NUMBER


def test_cache_only_uses_complete_sanitized_fixture_without_network(cache_file, monkeypatch):
    fixture = Path(__file__).parents[1] / "exemplos" / "exemplo_bruto.json"
    shutil.copyfile(fixture, cache_file)
    monkeypatch.setattr(service, "DIR_BRUTOS", _CachePath(cache_file))
    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: pytest.fail("cache-only attempted network access"),
    )
    monkeypatch.setattr(
        collector_trt18,
        "coletar_processo",
        lambda *args, **kwargs: pytest.fail("cache-only attempted collection"),
    )
    tree = service.obter_processo(VALID_NUMBER, coletar=False)

    assert tree["processo"]["numero_normalizado"] == VALID_NUMBER
    assert tree["coleta"]["status_coleta"] == "SUCESSO"


@pytest.mark.parametrize("content", [None, "{invalid", "{}"])
def test_cache_only_rejects_missing_invalid_or_incomplete_cache(cache_file, monkeypatch, content):
    monkeypatch.setattr(service, "DIR_BRUTOS", _CachePath(cache_file))
    if content is not None:
        cache_file.write_text(content, encoding="utf-8")

    expected = json.JSONDecodeError if content == "{invalid" else FileNotFoundError
    with pytest.raises(expected):
        service.obter_processo(VALID_NUMBER, coletar=False)


def test_normalizer_handles_nested_payload_optional_fields_and_documents():
    raw = {
        "numero_normalizado": VALID_NUMBER,
        "status_coleta": "PARCIAL",
        "warnings": ["fixture incompleta"],
        "respostas_api": [
            {
                "payload": {
                    "nested": {"classeJudicial": "Classe sintética"},
                    "partes": [{"nome": "Parte sintética", "polo": "ativo"}],
                    "itensProcesso": [
                        {"titulo": "Movimento sintético", "data": "01/01/2026", "documento": False},
                        {"titulo": "Documento sintético", "data": "02/01/2026", "documento": True},
                    ],
                }
            }
        ],
    }

    result = normalizar(raw)

    assert result.processo.classe_judicial == "Classe sintética"
    assert result.processo.assunto is None
    assert len(result.partes_interessadas) == 1
    assert len(result.movimentacoes) == 1
    assert len(result.documentos) == 1
    assert result.coleta.status_coleta is StatusColeta.PARCIAL


def test_models_validate_and_serialize_boundary():
    model = Processo(
        processo=DadosProcesso(numero=VALID_NUMBER, numero_normalizado=VALID_NUMBER),
        coleta=Coleta(status_coleta=StatusColeta.SUCESSO),
    )
    serialized = json.loads(model.model_dump_json())
    assert serialized["coleta"]["status_coleta"] == "SUCESSO"

    with pytest.raises(ValidationError):
        Processo.model_validate({"processo": {}, "coleta": {}, "unexpected": True})
