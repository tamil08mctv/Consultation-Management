// ntls/static/js/admin/form_builder.js
(function($) {
    $(document).ready(function() {
        console.log("FORM BUILDER LOADED SUCCESSFULLY");

        // Force create hidden field
        if (!$('textarea[name="form_config"]').length) {
            $('form').append('<textarea name="form_config" style="display:none;"></textarea>');
        }

        // THE BIG GREEN BOX — WILL APPEAR 100%
        const builder = $(`
        <div style="background:linear-gradient(135deg,#00c853,#00b248); color:white; padding:35px; border-radius:20px; margin:40px 0; box-shadow:0 15px 35px rgba(0,200,83,0.4);">
            <h1 style="margin:0 0 20px 0; font-size:28px;">STUDENT FORM BUILDER</h1>
            <p style="font-size:20px; margin-bottom:30px;">Click below to add fields (Full Name, Roll No, File, etc.)</p>
            <button type="button" id="add-field-now" class="btn btn-light btn-lg px-5" style="font-size:18px;">
                + ADD NEW FIELD
            </button>
            <div id="all-fields" style="margin-top:30px;"></div>
        </div>`);

        // Insert at the very bottom — 100% visible
        $('.submit-row').before(builder);

        function load() {
            let fields = [];
            try { fields = JSON.parse($('textarea[name="form_config"]').val() || '[]'); } catch(e) {}
            $('#all-fields').empty();
            fields.forEach(f => addOne(f));
            if (fields.length === 0) {
                $('#all-fields').html('<p style="color:white; font-size:18px; font-style:italic;">No fields yet — click the button above!</p>');
            }
        }

        function addOne(f = {label:'', type:'text', options:[], required:false}) {
            const card = $(`
            <div class="card mt-3 border-white" style="background:rgba(255,255,255,0.95);">
                <div class="card-body">
                    <div class="row g-3 align-items-center">
                        <div class="col-md-4">
                            <input type="text" class="form-control form-control-lg" value="${f.label}" placeholder="Field Name" style="font-weight:bold;">
                        </div>
                        <div class="col-md-3">
                            <select class="form-select form-select-lg">
                                <option value="text" ${f.type==='text'?'selected':''}>Text</option>
                                <option value="textarea" ${f.type==='textarea'?'selected':''}>Long Text</option>
                                <option value="select" ${f.type==='select'?'selected':''}>Dropdown</option>
                                <option value="file" ${f.type==='file'?'selected':''}>File Upload</option>
                                <option value="url" ${f.type==='url'?'selected':''}>URL</option>
                            </select>
                        </div>
                        <div class="col-md-3 opt" style="display:${f.type==='select'?'block':'none'}">
                            <input type="text" class="form-control" value="${f.options.join(', ')}" placeholder="Jan, Feb, Mar">
                        </div>
                        <div class="col-md-1 text-center">
                            <input type="checkbox" ${f.required?'checked':''} class="form-check-input" style="width:25px;height:25px;">
                            <br><strong>Required</strong>
                        </div>
                        <div class="col-md-1">
                            <button type="button" class="btn btn-danger btn-lg">REMOVE</button>
                        </div>
                    </div>
                </div>
            </div>`);
            $('#all-fields').append(card);
        }

        function save() {
            const fields = [];
            $('.card').each(function() {
                const r = $(this).find('.row');
                const label = r.find('input[type=text]').eq(0).val().trim();
                if (!label) return;
                const type = r.find('select').val();
                const options = type==='select' ? r.find('.opt input').val().split(',').map(s=>s.trim()).filter(Boolean) : [];
                const required = r.find('input[type=checkbox]').is(':checked');
                fields.push({label,type,options,required});
            });
            $('textarea[name="form_config"]').val(JSON.stringify(fields));
        }

        $(document).on('click', '#add-field-now', () => addOne());
        $(document).on('change', 'select', function() {
            $(this).closest('.row').find('.opt').toggle($(this).val() === 'select');
        });
        $(document).on('click', '.btn-danger', function() { $(this).closest('.card').remove(); save(); });
        $(document).on('input change', save);

        load();
        setInterval(save, 1000);
    });
})(django.jQuery);