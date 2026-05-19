"""单元测试：工具函数（验证器、帮助函数）"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../project/backend')))

import pytest
from utils import (
    validate_student_id, validate_email, validate_password,
    validate_price, validate_phone, validate_rating,
    allowed_file, paginate
)


class TestStudentId:
    def test_valid_10_digit_22023(self):
        assert validate_student_id('2202300001') == True
        assert validate_student_id('2202399999') == True

    def test_invalid_prefix(self):
        assert validate_student_id('2201300001') == False

    def test_too_short(self):
        assert validate_student_id('220231') == False

    def test_too_long(self):
        assert validate_student_id('22023000010') == False

    def test_contains_letters(self):
        assert validate_student_id('22023abcde') == False

    def test_empty(self):
        assert validate_student_id('') == False


class TestEmail:
    @pytest.mark.parametrize('email', [
        'test@qq.com', 'test@163.com',
        'abc123@qq.com', 'user+name@163.com',
        'a@qq.com',
    ])
    def test_valid_emails(self, email):
        assert validate_email(email) == True

    @pytest.mark.parametrize('email', [
        'test@gmail.com', 'test@outlook.com',
        'test@126.com', 'noatsign',
        '', '@qq.com', 'user@',
    ])
    def test_invalid_emails(self, email):
        assert validate_email(email) == False


class TestPassword:
    @pytest.mark.parametrize('pw', [
        '123456', 'abcdef', 'pass123', 'a' * 64,
    ])
    def test_valid_passwords(self, pw):
        assert validate_password(pw) == True

    @pytest.mark.parametrize('pw', [
        '', '12345', 'a' * 65,
    ])
    def test_invalid_passwords(self, pw):
        assert validate_password(pw) == False


class TestPrice:
    @pytest.mark.parametrize('price', [0, 0.01, 1, 100, 9999.99, 100000])
    def test_valid_prices(self, price):
        assert validate_price(price) == True

    @pytest.mark.parametrize('price', [-1, -0.01, 'abc', None, ''])
    def test_invalid_prices(self, price):
        assert validate_price(price) == False


class TestPhone:
    def test_valid_phone(self):
        assert validate_phone('13800138000') == True

    def test_empty_phone(self):
        assert validate_phone('') == True

    @pytest.mark.parametrize('phone', [
        '12345', '1380013800', '138001380000',
        'abc',
    ])
    def test_invalid_phones(self, phone):
        assert validate_phone(phone) == False


class TestRating:
    @pytest.mark.parametrize('r', [1, 2, 3, 4, 5])
    def test_valid_ratings(self, r):
        assert validate_rating(r) == True

    @pytest.mark.parametrize('r', [0, 6, -1, 'abc', None])
    def test_invalid_ratings(self, r):
        assert validate_rating(r) == False


class TestAllowedFile:
    def test_valid_extensions(self):
        for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            assert allowed_file(f'photo.{ext}') == True

    def test_invalid_extensions(self):
        for ext in ['exe', 'pdf', 'doc', 'svg', '', 'py']:
            assert allowed_file(f'file.{ext}') == False

    def test_no_extension(self):
        assert allowed_file('filename') == False
