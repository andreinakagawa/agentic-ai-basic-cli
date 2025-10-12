"""Tests for command parser."""


from src.cli.parser import parse_input, _levenshtein_distance, _suggest_similar_command


class TestLevenshteinDistance:
    """Test suite for Levenshtein distance calculation."""

    def test_identical_strings(self):
        """Test distance between identical strings."""
        assert _levenshtein_distance("hello", "hello") == 0
        assert _levenshtein_distance("", "") == 0

    def test_one_empty_string(self):
        """Test distance when one string is empty."""
        assert _levenshtein_distance("hello", "") == 5
        assert _levenshtein_distance("", "world") == 5

    def test_single_character_difference(self):
        """Test distance with single character changes."""
        # Substitution
        assert _levenshtein_distance("cat", "bat") == 1
        # Insertion
        assert _levenshtein_distance("cat", "cats") == 1
        # Deletion
        assert _levenshtein_distance("cats", "cat") == 1

    def test_multiple_character_differences(self):
        """Test distance with multiple character changes."""
        assert _levenshtein_distance("kitten", "sitting") == 3
        assert _levenshtein_distance("saturday", "sunday") == 3

    def test_completely_different_strings(self):
        """Test distance between completely different strings."""
        dist = _levenshtein_distance("abc", "xyz")
        assert dist == 3

    def test_case_sensitive(self):
        """Test that comparison is case-sensitive."""
        assert _levenshtein_distance("Hello", "hello") == 1


class TestSuggestSimilarCommand:
    """Test suite for command suggestion logic."""

    def test_suggest_exact_match_lowercase(self):
        """Test suggestion for exact match (different case)."""
        # Note: function uses lower() internally
        suggestion = _suggest_similar_command("exit")
        assert suggestion == "exit"

    def test_suggest_one_typo(self):
        """Test suggestion for one-character typo."""
        assert _suggest_similar_command("exot") == "exit"  # One substitution
        assert _suggest_similar_command("exi") == "exit"   # One deletion
        assert _suggest_similar_command("exitt") == "exit" # One insertion

    def test_suggest_two_typos(self):
        """Test suggestion for two-character typos."""
        assert _suggest_similar_command("exat") == "exit"  # Two substitutions (within threshold)
        assert _suggest_similar_command("hlp") == "help"   # Two deletions

    def test_no_suggestion_too_different(self):
        """Test no suggestion for very different commands."""
        # More than 2 edits away
        assert _suggest_similar_command("xyz") is None
        assert _suggest_similar_command("completely_different") is None

    def test_suggest_closest_match(self):
        """Test that closest match is suggested when multiple possibilities."""
        # "halp" is 1 edit from "help", more from others
        assert _suggest_similar_command("halp") == "help"

    def test_suggest_case_insensitive(self):
        """Test that suggestion is case-insensitive."""
        assert _suggest_similar_command("EXIT") == "exit"
        assert _suggest_similar_command("Help") == "help"


class TestParseInput:
    """Test suite for parse_input function."""

    def test_parse_exit_command(self):
        """Test parsing /exit command."""
        cmd_type, arg = parse_input("/exit")
        assert cmd_type == "exit"
        assert arg is None

    def test_parse_help_command(self):
        """Test parsing /help command."""
        cmd_type, arg = parse_input("/help")
        assert cmd_type == "help"
        assert arg is None

    def test_parse_session_command(self):
        """Test parsing /session command."""
        cmd_type, arg = parse_input("/session")
        assert cmd_type == "session"
        assert arg is None

    def test_parse_export_command_no_filename(self):
        """Test parsing /export command without filename."""
        cmd_type, arg = parse_input("/export")
        assert cmd_type == "export"
        assert arg is None

    def test_parse_export_command_with_filename(self):
        """Test parsing /export command with filename."""
        cmd_type, arg = parse_input("/export my_chat.txt")
        assert cmd_type == "export"
        assert arg == "my_chat.txt"

    def test_parse_export_command_with_path(self):
        """Test parsing /export command with file path."""
        cmd_type, arg = parse_input("/export /path/to/file.txt")
        assert cmd_type == "export"
        assert arg == "/path/to/file.txt"

    def test_parse_text_input(self):
        """Test parsing regular text input."""
        cmd_type, arg = parse_input("Hello, how are you?")
        assert cmd_type == "text"
        assert arg == "Hello, how are you?"

    def test_parse_empty_input(self):
        """Test parsing empty input."""
        cmd_type, arg = parse_input("")
        assert cmd_type == "text"
        assert arg == ""

    def test_parse_whitespace_input(self):
        """Test parsing whitespace-only input."""
        cmd_type, arg = parse_input("   ")
        assert cmd_type == "text"
        assert arg == ""

    def test_parse_input_with_leading_whitespace(self):
        """Test parsing input with leading whitespace."""
        cmd_type, arg = parse_input("  /help  ")
        assert cmd_type == "help"
        assert arg is None

    def test_parse_input_with_trailing_whitespace(self):
        """Test parsing text with trailing whitespace."""
        cmd_type, arg = parse_input("Hello world  ")
        assert cmd_type == "text"
        assert arg == "Hello world  "  # Preserves original input for text

    def test_parse_unknown_command(self):
        """Test parsing unknown command."""
        cmd_type, arg = parse_input("/unknown")
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)
        assert arg["error"] == "unknown_command"
        assert arg["command"] == "unknown"

    def test_parse_unknown_command_with_suggestion(self):
        """Test parsing unknown command that has a suggestion."""
        cmd_type, arg = parse_input("/exot")  # Similar to /exit
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)
        assert arg["error"] == "unknown_command"
        assert arg["command"] == "exot"
        assert "suggestion" in arg
        assert arg["suggestion"] == "exit"

    def test_parse_unknown_command_no_suggestion(self):
        """Test parsing unknown command with no close match."""
        cmd_type, arg = parse_input("/xyz123")
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)
        assert arg["error"] == "unknown_command"
        assert arg["command"] == "xyz123"
        assert "suggestion" not in arg

    def test_parse_command_case_sensitive(self):
        """Test that commands are case-sensitive."""
        # /exit works
        cmd_type, _ = parse_input("/exit")
        assert cmd_type == "exit"

        # /EXIT does not
        cmd_type, arg = parse_input("/EXIT")
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)

    def test_parse_text_starting_with_slash_in_content(self):
        """Test text that contains slash but not as command."""
        cmd_type, arg = parse_input("The URL is http://example.com")
        assert cmd_type == "text"
        assert arg == "The URL is http://example.com"

    def test_parse_multiline_text(self):
        """Test parsing text with newlines."""
        text = "Line 1\nLine 2\nLine 3"
        cmd_type, arg = parse_input(text)
        assert cmd_type == "text"
        assert arg == text

    def test_parse_text_with_special_characters(self):
        """Test parsing text with special characters."""
        text = "Special chars: !@#$%^&*()_+-={}[]|:;<>?,./"
        cmd_type, arg = parse_input(text)
        assert cmd_type == "text"
        assert arg == text

    def test_parse_export_with_spaces_in_filename(self):
        """Test /export with filename containing spaces."""
        cmd_type, arg = parse_input("/export my chat log.txt")
        assert cmd_type == "export"
        assert arg == "my chat log.txt"

    def test_parse_long_text_input(self):
        """Test parsing very long text input."""
        long_text = "This is a long message. " * 100
        cmd_type, arg = parse_input(long_text)
        assert cmd_type == "text"
        assert arg == long_text

    def test_parse_command_with_extra_args_ignored(self):
        """Test that commands with extra arguments handle correctly."""
        # /help with extra text - treated as unknown command
        cmd_type, arg = parse_input("/help me please")
        assert cmd_type == "unknown_command"  # Starts with / but not exact match
        assert isinstance(arg, dict)

        # /exit with extra text - also unknown command
        cmd_type, arg = parse_input("/exit now")
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)

    def test_parse_slash_only(self):
        """Test parsing just a slash."""
        cmd_type, arg = parse_input("/")
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)
        assert arg["command"] == ""

    def test_parse_export_multiword_filename(self):
        """Test /export with complex filename."""
        cmd_type, arg = parse_input("/export chat_2024_01_15.txt")
        assert cmd_type == "export"
        assert arg == "chat_2024_01_15.txt"

    def test_parse_numbers_as_text(self):
        """Test parsing numbers as text."""
        cmd_type, arg = parse_input("12345")
        assert cmd_type == "text"
        assert arg == "12345"

    def test_parse_emoji_text(self):
        """Test parsing text with emojis."""
        text = "Hello! 👋 How are you? 😊"
        cmd_type, arg = parse_input(text)
        assert cmd_type == "text"
        assert arg == text

    def test_parse_code_snippet(self):
        """Test parsing code snippet."""
        code = "def hello():\n    print('Hello world')"
        cmd_type, arg = parse_input(code)
        assert cmd_type == "text"
        assert arg == code


class TestParseInputEdgeCases:
    """Test edge cases for parse_input."""

    def test_parse_unicode_text(self):
        """Test parsing Unicode text."""
        text = "Héllo wörld! 你好世界"
        cmd_type, arg = parse_input(text)
        assert cmd_type == "text"
        assert arg == text

    def test_parse_export_with_extension(self):
        """Test /export with various file extensions."""
        for ext in [".txt", ".md", ".log", ".json"]:
            cmd_type, arg = parse_input(f"/export chat{ext}")
            assert cmd_type == "export"
            assert arg == f"chat{ext}"

    def test_parse_very_long_command(self):
        """Test parsing very long unknown command."""
        cmd_type, arg = parse_input("/" + "x" * 100)
        assert cmd_type == "unknown_command"
        assert isinstance(arg, dict)

    def test_parse_tabs_and_spaces(self):
        """Test parsing with tabs and mixed whitespace."""
        cmd_type, arg = parse_input("\t/help\t")
        assert cmd_type == "help"

        cmd_type, arg = parse_input("\t  /export  \t filename.txt  \t")
        assert cmd_type == "export"
        assert arg == "filename.txt"


class TestParserIntegration:
    """Integration tests for the parser."""

    def test_parse_conversation_flow(self):
        """Test parsing a realistic conversation flow."""
        inputs = [
            ("Hello!", "text", "Hello!"),
            ("/help", "help", None),
            ("What can you do?", "text", "What can you do?"),
            ("/session", "session", None),
            ("Thanks!", "text", "Thanks!"),
            ("/export my_chat.txt", "export", "my_chat.txt"),
            ("/exit", "exit", None),
        ]

        for user_input, expected_type, expected_arg in inputs:
            cmd_type, arg = parse_input(user_input)
            assert cmd_type == expected_type
            assert arg == expected_arg

    def test_parse_all_known_commands(self):
        """Test parsing all known commands."""
        known_commands = {
            "/exit": ("exit", None),
            "/help": ("help", None),
            "/session": ("session", None),
            "/export": ("export", None),
            "/export file.txt": ("export", "file.txt"),
        }

        for input_str, (expected_type, expected_arg) in known_commands.items():
            cmd_type, arg = parse_input(input_str)
            assert cmd_type == expected_type, f"Failed for input: {input_str}"
            assert arg == expected_arg, f"Failed for input: {input_str}"
