import sys
import argparse
import unittest
from unittest.mock import patch
from pathlib import Path

# Inyección de dependencias de la raíz de composición (Subir 3 niveles hasta translator_pdf)
sys.path.append(str(Path(__file__).resolve().parents[2]))

from apps.cli.main import main  # noqa: E402

class TestCLIRoutingAndArgparse(unittest.TestCase):

    @patch("apps.cli.main.parse_arguments")
    @patch("apps.cli.main.handle_translate")
    def test_translate_subcommand_routing(self, mock_handle, mock_parse):
        """Verifica que el subcomando 'translate' procese los argumentos correctamente."""
        args = argparse.Namespace(
            command="translate", 
            file_path="dummy.pdf", 
            job_id="job_unittest",
            func=mock_handle
        )
        mock_parse.return_value = args
        
        main()
        
        mock_handle.assert_called_once_with(args)

    @patch("apps.cli.main.parse_arguments")
    @patch("apps.cli.main.handle_resume")
    def test_resume_subcommand_routing(self, mock_handle, mock_parse):
        """Verifica que 'resume' capture el ID y el Hash y delegue al handler."""
        args = argparse.Namespace(
            command="resume", 
            document_id="doc_123", 
            ast_hash="hash_abc",
            func=mock_handle
        )
        mock_parse.return_value = args
        
        main()
        
        mock_handle.assert_called_once_with(args)

    @patch("apps.cli.main.parse_arguments")
    @patch("apps.cli.main.handle_sweep")
    def test_sweep_subcommand_routing(self, mock_handle, mock_parse):
        """Verifica el enrutamiento limpio del comando sweep."""
        args = argparse.Namespace(
            command="sweep",
            func=mock_handle
        )
        mock_parse.return_value = args
        
        main()
        
        mock_handle.assert_called_once_with(args)

    @patch("apps.cli.main.parse_arguments")
    @patch("apps.cli.main.handle_status")
    def test_status_subcommand_routing(self, mock_handle, mock_parse):
        """Verifica que 'status' capture los parámetros estructurales de consulta."""
        args = argparse.Namespace(
            command="status", 
            document_id="doc_777", 
            ast_hash="hash_xyz",
            func=mock_handle
        )
        mock_parse.return_value = args
        
        main()
        
        mock_handle.assert_called_once_with(args)

if __name__ == "__main__":
    unittest.main()