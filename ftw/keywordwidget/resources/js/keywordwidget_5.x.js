require([
  'jquery', 'keywordwidget_select2_js'
], function($, kwwSelect2) {
    'use strict';

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

        // Copy of code from select2 (jquery.select2 to be precise) as we can't use the jQuery plugin
        // $.fn.select2 as it is the wrong version
        $(widget).each(function() {
            var instanceOptions = $.extend(true, {}, config);

            var instance = new kwwSelect2($(this), instanceOptions);
        });
        $(widget).on('change', function(event){
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
    $(window).on('load', function(){
      $('.keyword-widget:visible').each(function(index, widget){
        window.ftwKeywordWidget.initWidget($(widget));
      });
    });

    // select2 has problems getting the correct width of the placeholder element if the content is hidden and select2 gets initialized.
    // See https://github.com/select2/select2/issues/291
    const selector = "form.enableFormTabbing > nav.autotoc-nav a, select.formTabs a, ul.formTabs a";
    $(document).on('mouseup', selector ,function (e) {
      setTimeout(function(){
        $('.keyword-widget:visible').each(function(index, widget){
          window.ftwKeywordWidget.initWidget($(widget));
        });
      }, 10);
    });

    $(document).on("onLoad OverlayContentReloaded", ".overlay", function() {
      $('.keyword-widget:visible').each(function(index, widget){
        window.ftwKeywordWidget.initWidget($(widget));
      });
    });

    $(document).on('focus', '.keyword-widget ~ .select2 .select2-selection.select2-selection--single', function(event){

      // Rough copy of code from select2 (jquery.select2) as we can't use the jQuery plugin
      // $.fn.select2 as it is the wrong version
      $(this).parents('.select2-container').prev().each(function() {
        // FIXME - this call should maybe respect more of the select2 configuration
        kwwSelect2($(this), 'open');
      });
    });

    return self;

});
