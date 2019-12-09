require([
  'jquery'
], function($) {
    'use strict';

    // Plone currently loads select2 v3.5
    var ploneVersionSelect2 = $.fn.select2 || null;

    if (ploneVersionSelect2) {
        delete $.fn.select2;
    }


    require([
      'select2'
    ], function(select2) {

        // Store the version we've just loaded for our event handlers to use
        $.fn.ftwKwWidgetSelect2 = $.fn.select2;

        var self = {};
        var templates = {};


        function init() {

            // Special template to indicate new terms
            registerTemplate("defaultResultTemplate", function (widget) {
              return function (data) {
                if (!data.loading && !data._resultId) {
                    return $('<span class="newTag" />')
                    .text(data.text)
                    .append($('<span class="newTagHint" />').text(widget.data("select2config").i18n.label_new));
                } else {
                    return data.text;
                }
              };
            });
            // Required for event handlers below - which need the correct version of select2
            window.ftwKeywordWidget = self;

            $(document).trigger("ftwKeywordWidgetInit");
        }

        function registerTemplate(name, templateFunction) {
            if (templates.hasOwnProperty(name)) {
                console.warn("A template with the name '" + name + "' is already registered.");
                return;
            }
            if (!$.isFunction(templateFunction)) {
                console.warn("The given template is not a function. A template needs to be a function.");
                return;
            }
            templates[name] = templateFunction;
        }

        function getTemplate(name, fallback, widget) {
            if (templates.hasOwnProperty(name)) {
                return templates[name](widget);
            } else if (templates.hasOwnProperty(fallback)) {
                return templates[fallback](widget);
            }
            return null;
        }

        function setSelect2Template(config, name, template) {
            if (!template) {
                return;
            }
            config[name] = template;
        }

        function initWidget(widget) {
            var config = widget.data("select2config");
            var i18n = config.i18n;
            var ajaxOptions = widget.data("ajaxoptions");
            var templateSelection = widget.data("templateselection");
            var templateResult = widget.data("templateresult");

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

            // Register templateResult
            setSelect2Template(config, "templateResult",
                               self.getTemplate(templateResult, "defaultResultTemplate", widget));

            // Register templateSelection
            setSelect2Template(config, "templateSelection",
                               self.getTemplate(templateSelection, "defaultSelectionTemplate", widget));

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

            $(widget).ftwKwWidgetSelect2(config).on('change', function(event){
                var newTermsField = $(this).parent().find('[id$="_new"]');
                if (newTermsField.length === 0) {
                  return;
                }

                // They're probably not really selected but added manually.
                var newAddedTerms = $.map($(this).find('[data-select2-tag="true"]'), function(val, i){ return val.value; });

                var allSelectedTerms = $(this).data('select2').val() || [];
                var newSelectedTerms = $.map(newAddedTerms, function(val, i){
                  if (allSelectedTerms.indexOf(val) !== -1) {
                    return val;
                  }
                });
                newTermsField.val(newSelectedTerms.join('\n'));
            }).parent().addClass(config.tags ? 'select2tags' : '');

            $(document).trigger("ftwKeywordWidgetInitWidget", [widget]);
        }

        self.initWidget = initWidget;
        self.registerTemplate = registerTemplate;
        self.getTemplate = getTemplate;
        self.init = init;

        // No need to wait for window.load() with requirejs
        init();
        $('.keyword-widget:visible').each(function(index, widget){
          window.ftwKeywordWidget.initWidget($(widget));
        });

        // select2 has problems getting the correct width of the placeholder element if the content is hidden and select2 gets initialized.
        // See https://github.com/select2/select2/issues/291
        $("form.enableFormTabbing > nav.autotoc-nav a, select.formTabs a, ul.formTabs a").on("click", function (e, index) {
          $('.keyword-widget:visible').each(function(index, widget){
            window.ftwKeywordWidget.initWidget($(widget));
          });
        });

        $(document).on("onLoad OverlayContentReloaded", ".overlay", function() {
          $('.keyword-widget:visible').each(function(index, widget){
            window.ftwKeywordWidget.initWidget($(widget));
          });
        });

        $(document).on('focus', '.select2-selection.select2-selection--single', function(event){
          $(this).parents('.select2-container').prev().ftwKwWidgetSelect2('open');
        });

        if (ploneVersionSelect2) {
            delete $.fn.select2;
            $.fn.select2 = ploneVersionSelect2;
        }

        return self;

    });

});
