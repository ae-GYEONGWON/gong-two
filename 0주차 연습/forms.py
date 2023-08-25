from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username =  StringField("이름", render_kw={"placeholder": "이름을 입력해주세요"},
                            validators=[DataRequired(), Length(min=2, max=20)])
    email =  StringField("이메일", render_kw={"placeholder": "이메일을 입력해주세요"}, 
                            validators=[DataRequired(), Email()])
    password = PasswordField("비밀번호 입력", render_kw={"placeholder": "비밀번호를 입력해주세요"},
                            validators=[DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField("비밀번호 확인", render_kw={"placeholder": "비밀번호를 다시 입력해주세요"},
                            validators=[DataRequired(), EqualTo("password")] )
    account = StringField("계좌번호", render_kw={"placeholder": "계좌번호를 입력해주세요"},
                            validators=[DataRequired(), Length(min=10, max=13)])
    submit = SubmitField("회원가입")

class LoginForm(FlaskForm):
    id =  StringField("아이디", render_kw={"placeholder": "이메일을 입력해주세요"}, 
                            validators=[DataRequired(), Email()])
    password = PasswordField("비밀번호 입력", render_kw={"placeholder": "비밀번호를 입력해주세요"},
                            validators=[DataRequired(), Length(min=4, max=20)])
    login = SubmitField("로그인")