from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {
    "Grupo",
    "Processo",
    "Em_CN",
    "Em_Sent",
    "Em_TBaix",
    "Em_CPL",
    "Orgao",
    "Classe",
    "Data_ajuizamento",
    "Data_primeiro_julgamento",
    "Datas_sentenca",
    "Datas_baixa",
}

DEFAULT_META_ID = "avaliacao_trt18"
DEFAULT_ANO = 2026


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Injeta uma amostra CSV em um banco SQLite temporario e executa "
            "a avaliacao de impacto processual usando o codigo real do projeto."
        )
    )

    parser.add_argument(
        "csv_path",
        type=Path,
        help="Caminho para TRT18_cruzamento_amostras.csv.",
    )

    parser.add_argument(
        "--meta-id",
        default=DEFAULT_META_ID,
        help=(
            "Identificador de meta repassado ao sistema "
            f"(padrao: {DEFAULT_META_ID})."
        ),
    )

    parser.add_argument(
        "--ano",
        type=int,
        default=DEFAULT_ANO,
        help=f"Ano repassado ao sistema (padrao: {DEFAULT_ANO}).",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Diretorio para resultados CSV/JSON.",
    )

    parser.add_argument(
        "--manter-banco",
        action="store_true",
        help=(
            "Mantem uma copia do banco de avaliacao em "
            "outputs/avaliacao_trt18.sqlite3."
        ),
    )

    return parser.parse_args()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _prepare_project_imports(database_path: Path) -> None:
    chatbot_dir = _repo_root() / "chatbot_processual_ai"

    if not chatbot_dir.is_dir():
        raise RuntimeError(
            f"Diretorio do chatbot nao encontrado: {chatbot_dir}"
        )

    # IMPORTANTÍSSIMO:
    # LOCAL_DB_PATH precisa ser definido antes do import de config.py /
    # process_repository.py, pois o repository importa essa configuração
    # durante o carregamento do módulo.
    os.environ["LOCAL_DB_PATH"] = str(database_path.resolve())

    sys.path.insert(0, str(chatbot_dir))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV nao encontrado: {path}")

    last_error: UnicodeDecodeError | None = None

    # O arquivo recebido atualmente está em uma codificação compatível
    # com CP1252, mas aceitamos UTF-8 primeiro para não amarrar o módulo
    # à codificação específica dessa amostra.
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open(
                "r",
                encoding=encoding,
                newline="",
            ) as handle:
                reader = csv.DictReader(
                    handle,
                    delimiter=";",
                )

                fieldnames = set(reader.fieldnames or [])
                missing = REQUIRED_COLUMNS - fieldnames

                if missing:
                    missing_text = ", ".join(sorted(missing))
                    raise ValueError(
                        "CSV sem colunas obrigatorias: "
                        f"{missing_text}"
                    )

                return [
                    {
                        key: (value or "").strip()
                        for key, value in row.items()
                    }
                    for row in reader
                ]

        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeError(
        f"Nao foi possivel decodificar o CSV: {last_error}"
    )


def _expected_bool(
    value: str,
    *,
    field: str,
    process_number: str,
) -> bool:
    normalized = value.strip().upper()

    if normalized == "SIM":
        return True

    if normalized == "NAO":
        return False

    raise ValueError(
        f"Valor invalido em {field} para {process_number}: "
        f"{value!r}. Esperado SIM ou NAO."
    )


def _split_dates(value: str) -> list[str]:
    return [
        part.strip()
        for part in value.split("|")
        if part.strip()
    ]


def _build_mock_tree(
    row: dict[str, str],
) -> dict[str, Any]:
    process_number = row["Processo"]

    normalized_number = re.sub(
        r"\D",
        "",
        process_number,
    )

    if len(normalized_number) != 20:
        raise ValueError(
            f"Numero CNJ invalido na amostra: {process_number}"
        )

    movements: list[dict[str, Any]] = []
    order = 1

    first_judgment = row["Data_primeiro_julgamento"]

    if first_judgment:
        movements.append(
            {
                "ordem": order,
                "data": first_judgment,
                "descricao": "Julgamento",
                "complemento": (
                    "Evento derivado de "
                    "Data_primeiro_julgamento da amostra."
                ),
                "referencia": "mock_avaliacao",
            }
        )

        order += 1

    for date in _split_dates(row["Datas_sentenca"]):
        movements.append(
            {
                "ordem": order,
                "data": date,
                "descricao": "Sentenca",
                "complemento": (
                    "Evento derivado de "
                    "Datas_sentenca da amostra."
                ),
                "referencia": "mock_avaliacao",
            }
        )

        order += 1

    for date in _split_dates(row["Datas_baixa"]):
        movements.append(
            {
                "ordem": order,
                "data": date,
                "descricao": "Baixa",
                "complemento": (
                    "Evento derivado de "
                    "Datas_baixa da amostra."
                ),
                "referencia": "mock_avaliacao",
            }
        )

        order += 1

    return {
        "processo": {
            "numero": process_number,
            "numero_normalizado": normalized_number,
            "classe_judicial": row["Classe"] or None,
            "assunto": None,
            "orgao_julgador": row["Orgao"] or None,
            "unidade": None,
            "jurisdicao": None,
            "grau": None,
            "data_autuacao": (
                row["Data_ajuizamento"] or None
            ),
            "valor_causa": None,
            "situacao": None,
        },

        "partes_interessadas": [],

        "movimentacoes": movements,

        "documentos": [],

        "pendencias": [],

        "coleta": {
            "fonte": "TRT18_cruzamento_amostras.csv",
            "status_coleta": "MOCK_AVALIACAO",
            "warnings": [
                (
                    "Arvore sintetica criada exclusivamente "
                    "para avaliacao offline; nao representa "
                    "coleta real do PJe."
                )
            ],
            "erros": [],
        },
    }


def _flag_to_text(
    value: bool | None,
) -> str:
    if value is True:
        return "SIM"

    if value is False:
        return "NAO"

    return "INCONCLUSIVO"


def _build_result_row(
    source_row: dict[str, str],
    response: Any,
) -> dict[str, Any]:

    expected_new = _expected_bool(
        source_row["Em_CN"],
        field="Em_CN",
        process_number=source_row["Processo"],
    )

    expected_judged = _expected_bool(
        source_row["Em_Sent"],
        field="Em_Sent",
        process_number=source_row["Processo"],
    )

    expected_discharged = _expected_bool(
        source_row["Em_TBaix"],
        field="Em_TBaix",
        process_number=source_row["Processo"],
    )

    match_new = (
        response.conta_como_novo
        is expected_new
    )

    match_judged = (
        response.conta_como_julgado
        is expected_judged
    )

    match_discharged = (
        response.conta_como_baixado
        is expected_discharged
    )

    return {
        "grupo": source_row["Grupo"],
        "processo": source_row["Processo"],

        "esperado_cn": source_row["Em_CN"],
        "sistema_cn": _flag_to_text(
            response.conta_como_novo
        ),
        "acerto_cn": match_new,

        "esperado_sent": source_row["Em_Sent"],
        "sistema_sent": _flag_to_text(
            response.conta_como_julgado
        ),
        "acerto_sent": match_judged,

        "esperado_tbaix": source_row["Em_TBaix"],
        "sistema_tbaix": _flag_to_text(
            response.conta_como_baixado
        ),
        "acerto_tbaix": match_discharged,

        "esperado_cpl": source_row["Em_CPL"],
        "cpl_avaliado": False,

        "acerto_triplo": (
            match_new
            and match_judged
            and match_discharged
        ),

        "impacto": response.impacto,
        "motivo": response.motivo,

        "meses_cn_fonte": source_row.get(
            "Meses_CN",
            "",
        ),

        "datas_sentenca_fonte": (
            source_row["Datas_sentenca"]
        ),

        "datas_baixa_fonte": (
            source_row["Datas_baixa"]
        ),
    }


def _metric(
    results: list[dict[str, Any]],
    field: str,
) -> dict[str, Any]:

    hits = sum(
        1
        for row in results
        if row[field] is True
    )

    total = len(results)

    accuracy = (
        hits / total
        if total
        else 0.0
    )

    return {
        "acertos": hits,
        "total": total,
        "acuracia": round(
            accuracy,
            4,
        ),
        "acuracia_percentual": round(
            accuracy * 100,
            2,
        ),
    }


def _build_summary(
    results: list[dict[str, Any]],
    meta_id: str,
    ano: int,
) -> dict[str, Any]:

    by_group: dict[str, dict[str, Any]] = {}

    groups = sorted(
        {
            str(row["grupo"])
            for row in results
        }
    )

    for group in groups:
        group_rows = [
            row
            for row in results
            if row["grupo"] == group
        ]

        by_group[group] = {
            "casos": len(group_rows),

            "cn": _metric(
                group_rows,
                "acerto_cn",
            ),

            "sent": _metric(
                group_rows,
                "acerto_sent",
            ),

            "tbaix": _metric(
                group_rows,
                "acerto_tbaix",
            ),

            "triplo": _metric(
                group_rows,
                "acerto_triplo",
            ),
        }

    return {
        "meta_id": meta_id,
        "ano": ano,
        "total_processos": len(results),

        "cn": _metric(
            results,
            "acerto_cn",
        ),

        "sent": _metric(
            results,
            "acerto_sent",
        ),

        "tbaix": _metric(
            results,
            "acerto_tbaix",
        ),

        "triplo": _metric(
            results,
            "acerto_triplo",
        ),

        "cpl": {
            "avaliado": False,
            "motivo": (
                "O sistema atual nao possui "
                "indicador equivalente a Em_CPL."
            ),
        },

        "por_grupo": by_group,

        "observacoes": [
            (
                "Em_CN, Em_Sent, Em_TBaix e Grupo "
                "foram usados apenas como referencia "
                "de comparacao."
            ),
            (
                "O mock injetado foi construido somente "
                "com campos factuais da amostra: numero, "
                "orgao, classe e datas."
            ),
            (
                "O banco SQLite usado na execucao "
                "e temporario por padrao."
            ),
            (
                "A avaliacao executa o orquestrador "
                "e as regras existentes do chatbot "
                "sem altera-las."
            ),
        ],
    }


def _write_results(
    output_dir: Path,
    results: list[dict[str, Any]],
    summary: dict[str, Any],
) -> tuple[Path, Path]:

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        output_dir
        / "resultado_avaliacao.csv"
    )

    json_path = (
        output_dir
        / "resumo_avaliacao.json"
    )

    if results:
        with csv_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=list(
                    results[0].keys()
                ),
                delimiter=";",
            )

            writer.writeheader()
            writer.writerows(results)

    with json_path.open(
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            summary,
            handle,
            ensure_ascii=False,
            indent=2,
        )

    return csv_path, json_path


def _print_summary(
    summary: dict[str, Any],
    csv_path: Path,
    json_path: Path,
) -> None:

    print("\n=== Avaliacao TRT18 ===")

    print(
        f"Processos: "
        f"{summary['total_processos']}"
    )

    print(
        "CN: "
        f"{summary['cn']['acertos']}/"
        f"{summary['cn']['total']} "
        f"("
        f"{summary['cn']['acuracia_percentual']:.2f}%"
        f")"
    )

    print(
        "Sentenca/julgamento: "
        f"{summary['sent']['acertos']}/"
        f"{summary['sent']['total']} "
        f"("
        f"{summary['sent']['acuracia_percentual']:.2f}%"
        f")"
    )

    print(
        "Baixa: "
        f"{summary['tbaix']['acertos']}/"
        f"{summary['tbaix']['total']} "
        f"("
        f"{summary['tbaix']['acuracia_percentual']:.2f}%"
        f")"
    )

    print(
        "Acerto simultaneo dos 3 indicadores: "
        f"{summary['triplo']['acertos']}/"
        f"{summary['triplo']['total']} "
        f"("
        f"{summary['triplo']['acuracia_percentual']:.2f}%"
        f")"
    )

    print(
        "CPL: nao avaliado "
        "(sem indicador equivalente "
        "no sistema atual)."
    )

    print(
        f"Resultado detalhado: "
        f"{csv_path}"
    )

    print(
        f"Resumo: "
        f"{json_path}"
    )


def main() -> int:
    args = parse_args()

    rows = _read_csv(
        args.csv_path.resolve()
    )

    if not rows:
        raise ValueError(
            "O CSV nao possui linhas de dados."
        )

    with tempfile.TemporaryDirectory(
        prefix="trt18_avaliacao_"
    ) as temp_dir:

        database_path = (
            Path(temp_dir)
            / "avaliacao_trt18.sqlite3"
        )

        _prepare_project_imports(
            database_path
        )

        # Imports intencionalmente tardios.
        # LOCAL_DB_PATH já aponta para o
        # banco temporário neste momento.
        from orchestrators.hybrid_orchestrator import (
            run_process_meta_impact,
        )

        from services.process_repository import (
            ingest_processes,
        )

        mock_processes = [
            _build_mock_tree(row)
            for row in rows
        ]

        ingest_processes(
            mock_processes,
            source_name=args.csv_path.name,
        )

        results: list[
            dict[str, Any]
        ] = []

        for source_row in rows:
            response = (
                run_process_meta_impact(
                    source_row["Processo"],
                    args.meta_id,
                    args.ano,
                )
            )

            results.append(
                _build_result_row(
                    source_row,
                    response,
                )
            )

        summary = _build_summary(
            results,
            args.meta_id,
            args.ano,
        )

        csv_path, json_path = (
            _write_results(
                args.output_dir.resolve(),
                results,
                summary,
            )
        )

        if args.manter_banco:
            persistent_db = (
                args.output_dir.resolve()
                / "avaliacao_trt18.sqlite3"
            )

            persistent_db.write_bytes(
                database_path.read_bytes()
            )

            print(
                "Banco preservado "
                "para inspecao: "
                f"{persistent_db}"
            )

    _print_summary(
        summary,
        csv_path,
        json_path,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())