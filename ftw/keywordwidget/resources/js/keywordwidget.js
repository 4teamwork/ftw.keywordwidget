$(function() {

    function initSelect2(widget){
        var config = widget.data("select2config");
        var i18n = config.i18n;
        var ajaxOptions = widget.data("ajaxoptions");

        // Update language from Backend
        config.language = {
          noResults: function(){
            return i18n.label_no_result;
          },
          searching: function () {
            return i18n.label_searching;
          },
          loadingMore: function () {
            return i18n.label_loading_more;
          },
          inputTooShort: function (args) {
            var remainingChars = args.minimum - args.input.length;

            var message = i18n.label_tooshort_prefix + remainingChars + i18n.label_tooshort_postfix;

            return message;
          }
        };

        // Update placholder with translated string
        config.placeholder = i18n.label_placeholder;

        // Special template to indicate new terms
        config.templateResult = function (data) {
          if (!data.loading) {
            // Nested if, since we cannot use amp in a templage... grml... will change this soon.
            if (!data._resultId) {
                // Since this is hacked into a pt, we cannot use html tags :-(
                return $(document.createElement('span'))
                  .text(data.text)
                  .addClass('newTag')
                  .add($(document.createElement('span')).addClass('newTagHint').text(i18n.label_new));
              } else {
                return data.text;
              }              
            }
        };

        // Add and Update config for remote data
        if (ajaxOptions) {
          config.ajax = {
            data: function (params) {
              return {
                q: params.term,
                page: params.page || 1
              };
            },
            processResults: function (data, params) {
              params.page = params.page || 1;
              return data;
            },
            cache: true
          };

          $.extend(config.ajax, ajaxOptions);
        }

        $(widget).select2(config).on('change', function(event){
            var newTermsField = $(this).parent().find('[id$="_new"]');
            var newTerms = $(this).find('[data-select2-tag="true"]');
            var newTermsText = $.map(newTerms, function(val, i){ return val.value; });
            newTermsField.val(newTermsText.join('\n'));
        }).parent().addClass(config.tags ? 'select2tags' : '');
    }

    window.ftwKeywordWidgetInitSelect2 = initSelect2;

    $(window).load(function(){
      if ($().select2 === undefined) {
          console.warn('You need to make sure, that select2 jquery plugin is loaded!');
      } else {
          var widget = $('#<tal:widgetid replace="view/id" />');
          initSelect2(widget);
      }
    });

    $(document).on("onLoad OverlayContentReloaded", ".overlay", function() {
      $('.keyword-widget:visible').each(function(indes, widget){
        ftwKeywordWidgetInitSelect2($(widget));
      });

      // select2 has issues to get right width of the placeholder element if the content is hidden and select2 gets initialized.
      // See https://github.com/select2/select2/issues/291
      var tabs = $('select.formTabs, ul.formTabs');
      tabs.on("click", function (e, index) {
        $('.keyword-widget:visible').each(function(indes, widget){
          ftwKeywordWidgetInitSelect2($(widget));
        });
      });


    });

});
