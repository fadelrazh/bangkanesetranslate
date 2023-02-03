$(document).ready(function() {
    $('#translate_button').click(function() {
        var src_input_text = $('#source_text').val();
        var src_lang = $('#source_language').val();
        var tgt_lang = $('#target_language').val();

        $.post('/translate', {source_text: src_input_text, source_language: src_lang, target_language: tgt_lang}, function(data) {
            $('#target_text').val(data.translation);
        });
    });

    document.getElementById("source_language").addEventListener("change", function() {
        var source_language = this.value;
        var target_language = document.getElementById("target_language");
        for (var i = 0; i < target_language.options.length; i++) {
            target_language.options[i].style.display = "block";
            if (target_language.options[i].value === source_language) {
                target_language.options[i].style.display = "none";
            }
        }
    });
});