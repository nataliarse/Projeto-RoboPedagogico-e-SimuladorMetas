import unittest
from unittest.mock import patch

import bedrock_client
from services import norma_rag, normas_pgvector


class BuscaNormasPgvectorTestCase(unittest.TestCase):
    def test_busca_usa_embedding_do_bedrock_e_o_pgvector(self):
        trecho = {"meta": "Meta 1", "pagina": 5, "secao": "Esclarecimentos", "texto": "julgados", "score": 0.6}
        with patch.object(norma_rag, "NORMAS_BACKEND", "pgvector"), \
                patch.object(bedrock_client, "embed_text", return_value=[0.1, 0.2]) as embed, \
                patch.object(normas_pgvector, "buscar", return_value=[trecho]) as buscar:
            resultado = norma_rag.search_normas("o que é julgado", metas=["Meta 1"], top_k=2)

        self.assertEqual(resultado, [trecho])
        embed.assert_called_once_with("o que é julgado")
        vetor, metas, top_k, _ = buscar.call_args.args
        self.assertEqual((vetor, metas, top_k), ([0.1, 0.2], ["Meta 1"], 2))

    def test_falha_no_banco_devolve_lista_vazia_sem_derrubar_a_resposta(self):
        with patch.object(norma_rag, "NORMAS_BACKEND", "pgvector"), \
                patch.object(bedrock_client, "embed_text", return_value=[0.1]), \
                patch.object(normas_pgvector, "buscar", side_effect=normas_pgvector.NormasDBError("x")):
            self.assertEqual(norma_rag.search_normas("pergunta"), [])

    def test_falha_no_embedding_devolve_lista_vazia(self):
        with patch.object(norma_rag, "NORMAS_BACKEND", "pgvector"), \
                patch.object(bedrock_client, "embed_text", side_effect=bedrock_client.BedrockError("x")):
            self.assertEqual(norma_rag.search_normas("pergunta"), [])

    def test_indexacao_grava_todos_os_trechos_do_glossario(self):
        with patch.object(norma_rag, "NORMAS_BACKEND", "pgvector"), \
                patch.object(bedrock_client, "embed_text", return_value=[0.0, 1.0]), \
                patch.object(normas_pgvector, "indexar", side_effect=lambda t, v, f: len(t)) as indexar:
            total = norma_rag.index_normas()

        trechos, vetores, fonte = indexar.call_args.args
        self.assertEqual(total, len(trechos))
        self.assertEqual(len(vetores), len(trechos))
        self.assertGreater(total, 20)
        self.assertIn("Glossário das Metas", fonte)


class SecretDoBancoTestCase(unittest.TestCase):
    def test_monta_a_url_a_partir_dos_campos_do_secret(self):
        class _Cliente:
            def get_secret_value(self, SecretId):
                return {"SecretString": '{"username": "aluno", "password": "s3nh@/x", '
                                        '"host": "db.exemplo", "port": 5432, "dbname": "iesb"}'}

        with patch("boto3.client", return_value=_Cliente()):
            url = normas_pgvector._url_do_secret()
        self.assertEqual(url, "postgresql://aluno:s3nh%40/x@db.exemplo:5432/iesb")

    def test_literal_do_vetor_usa_colchetes(self):
        self.assertEqual(normas_pgvector._literal([1, 0.5]), "[1.0000000,0.5000000]")


if __name__ == "__main__":
    unittest.main()
