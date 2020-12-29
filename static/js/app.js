$(document).ready(function () {
    let active_page = ($('#page_selector').val() || 'coverage');
    let active_tab = active_page + '-tab';
    $('#' + active_page).addClass('active').addClass('show');
    $('#' + active_tab).addClass('active');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFToken', $('[name=csrfmiddlewaretoken]').val());
            }
        }
    });

    $('.type_floor').on('change', function (e) {
        let sel = $(e.target);
        $(sel.parent().parent()).find('.floor').toggle($(sel).val() === '4');
    });

    $('.floor').css('display', $('.type_floor').val() === '4' ? 'block' : 'none');

    $('#mortgage_form .NumberOfInsured').on('change', function (e) {
        mort_show_insured();
    });

    $('#mortgage_form .NumberOfTracks').on('change', function (e) {
        mort_show_tracks();
    });

    mort_show_insured();
    mort_show_tracks();

});

let csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

let mort_show_insured = function() {
    let int_val = Number($('#mortgage_form .NumberOfInsured').val());
    let ins_btns = $('#insurSelect .nav-link');
    for (let i = 0; i < ins_btns.length; i++) {
        if (i < int_val) {
            $(ins_btns[i]).removeClass('disabled');
        } else {
            $(ins_btns[i]).addClass('disabled');
        }
    }
};

let mort_show_tracks = function() {
    let int_val = Number($('#mortgage_form .NumberOfTracks').val());
    let track_btns = $('#trackSelect .nav-link');
    for (let i=0; i <track_btns.length; i++)
    {
        if (i<int_val) {
            $(track_btns[i]).removeClass('disabled');
        }
        else {
            $(track_btns[i]).addClass('disabled');
        }
    }
};

let get_proposal = function (e, form_id, url, res_elem_id) {
    let startTime = new Date();
    e.preventDefault();
    let form = $(form_id);
    let da = form.serializeArray();
    let data = {
        'own_client': true,
        'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val(),
    };
    for (let i = 0; i < da.length; i++) {
        data[da[i].name] = da[i].value;
    }
    if (url === '/coverage/') {
        data['LeftCountryInThreeYears'] = Boolean($('#LeftCountryInThreeYears').val());
        data['PassportIssuedInThreeYears'] = Boolean($('#PassportIssuedInThreeYears').val());
        delete(data['captcha_str']);
    }

    if (url === '/mortgage/') {
        let insured = $('#mortgage_form .NumberOfInsured').val();
        let ins_data = $('#insurData div.tab-pane.fade');
        let tracks = $('#mortgage_form .NumberOfTracks').val();
        let track_data = $('#trackData div.tab-pane.fade');
        data['ListOfInsured'] = [];
        for (let i = 0; i < Number(insured); i++) {
            data['ListOfInsured'].push({
                "BirthDate": $(ins_data[i]).find('.BirthDate').val(),
                "Gender":  $(ins_data[i]).find('.Gender').val(),
                "IsSmoking":  $(ins_data[i]).find('.IsSmoking').val(),
            });
        }
        data['ListOfTracks'] = [];

        for (let t = 0; t < Number(tracks); t++) {
            data['ListOfTracks'].push({
                "DesiredPeriod": Number($(track_data[t]).find('.DesiredPeriod').val()),
                "DesiredSum":  Number($(track_data[t]).find('.DesiredSum').val()),
                "InterestRate":  Number($(track_data[t]).find('.InterestRate').val() * 100),
                "InterestType":  Number($(track_data[t]).find('.InterestType').val()),
            });
        }
    }

    if ( url in ['/fullprop/', '/content/', '/building/']) {
        let type_floor_id ='#' + form_id[1] + '_type_floor';
        if ($(form.find(type_floor_id)).val() === '4') {
            data[form_id[1] + '_mid_floor'] = $(form.find('#' + form_id[1] + '_mid_floor')).val();
        }
        else {
            delete data[form_id[1] + '_mid_floor'];
        }
    }

    $($(res_elem_id).data('tab')).addClass('waiting');
    $(res_elem_id).find('label.timer').text('');
    $(res_elem_id).find('label.error').text('');
    $(res_elem_id).find('.send').addClass('disabled').attr('disabled', true);
    $(res_elem_id).find('.json-viewer').remove();
    let req_jV = new JSONViewer();
    let req_viewer = req_jV.getContainer();
    $(req_viewer).css('height','auto')
    $(res_elem_id).append(req_viewer);
    req_jV.showJSON(data, -1, 1);

    $.ajax({
        type: 'POST',
        async: true,
        url: url,
        data: JSON.stringify(data),
        cache: false,
        contentType: false,
        processData: false
    }).fail(function (response) {
        $($(res_elem_id).find('.send')).removeClass('disabled').attr('disabled', false);
        $($(res_elem_id).data('tab')).removeClass('waiting');
        $($(res_elem_id).find('pre.json-viewer > a.list-link')).click();
        let timer_lbl = $(res_elem_id).find('label.timer');
        timer_lbl.text((new Date()-startTime)/1000 + ' sec');
        if ( response.Message ){
            $('<label class="error badge badge-danger">' + response.Message + '</label>').insertBefore(timer_lbl);
        }
        if (response.responseText) {
            $(res_elem_id).append('<pre class="json-viewer">' + response.responseText + '</pre>');
        }
        $('.tab-pane.active button.send').focus();
    }).done(function (response) {

        // let exp_btns = $(res_elem_id).find('a.list-link.collapsed');
        $($(res_elem_id).find('button.send')).removeClass('disabled').attr('disabled', false);
        $($(res_elem_id).data('tab')).removeClass('waiting');
        let timer_lbl = $(res_elem_id).find('label.timer');
        timer_lbl.text((new Date()-startTime)/1000 + ' sec');
        if ( response.Message ){
            $('<label class="error badge badge-danger">' + response.Message + '</label>').insertBefore(timer_lbl);
        }
        let has_data = (response.data && response.data.length);
        $($(res_elem_id).find('pre.json-viewer > a.list-link')).click();
        let resp_jV = new JSONViewer();
        let resp_viewer = resp_jV.getContainer();
        $(res_elem_id).append(resp_viewer);
        req_jV.showJSON(data, -1, 0);
        resp_jV.showJSON(has_data ? response.data : response, -1, 2);
        $(resp_viewer).css('height', '75vh');
        // $('a.list-link.collapsed').each( function() {
        //     this.click();
        // });
        // }
        $('.tab-pane.active button.send').focus();
    });
    return false;
};

$('#content_data > .send').on('click', function (e) {
    get_proposal(e, '#content_form', '/content/', '#content_data');
});

$('#building_data > .send').on('click', function (e) {
    get_proposal(e, '#building_form', '/building/', '#building_data');
});

$('#fullprop_data > .send').on('click', function (e) {
    get_proposal(e, '#fullprop_form', '/fullprop/', '#fullprop_data');
});

$('#mortgage_data > .send').on('click', function (e) {
    get_proposal(e, '#mortgage_form', '/mortgage/', '#mortgage_data');
});

$('#life_data > .send').on('click', function (e) {
    get_proposal(e, '#life_form', '/life/', '#life_data');
});

$('#health_data > .send').on('click', function (e) {
    get_proposal(e, '#health_form', '/health/', '#health_data');
});

$('#coverage_data > .send').on('click', function (e) {
    get_proposal(e, '#coverage_form', '/coverage/', '#coverage_data');
});

$('#control_data > .send').on('click', function (e) {
    // get_proposal(e, '#control_form', '/control/', '#control_data');
});
