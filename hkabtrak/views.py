from datetime import datetime

from flask import render_template, Blueprint, current_app

from hkabtrak.absence_form import AbsenceForm
from hkabtrak.models import Class

valid_reasons = ['Absent', 'Late', 'Leaving Early', 'Absent for a Time', '欠席', '遅刻', '早退', '時間で欠席']

root_bp = Blueprint('root', __name__, template_folder='templates')


@root_bp.route('/', methods=['GET', 'POST'])
def index():
    form = AbsenceForm()

    default_course_choice = [('', '学年を選択してください')]
    form.class_id.choices = default_course_choice + [
        (cls.id, cls.name, {'data-instructions': cls.instructions or 'None'}) for cls in Class.query.all()
    ]

    classes = Class.query.all()
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('new_absence.html', form=form, today=today)


@root_bp.route('/thank_you')
def thank_you():
    return render_template('absence_submited.html')


@root_bp.route('/javascript-required')
def javascript_required():
    return render_template('javascript_required.html')
