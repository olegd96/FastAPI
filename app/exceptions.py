from fastapi import HTTPException, status


class BookingException(HTTPException):  # <-- наследуемся от HTTPException, который наследован от Exception
    status_code = 500  # <-- задаем значения по умолчанию
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"



class IncorrectEmailOrPasswordException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверная почта или пароль"

class IncorrectCurrentPasswordException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Неверный текущий пароль"


class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен истек"


class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"


class UserIsNotPresentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail = "Не осталось свободных номеров"


class DateFromCannotBeAfterDateTo(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Дата заезда не может быть позже даты выезда"

class UnverifiedEmailException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Неподтвержденный адрес электронной почты"


class CannotBookHotelForLongPeriod(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Невозможно забронировать отель сроком более месяца"

class CannotProcessCSV(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Не удалось обработать CSV файл"

class CannotAddDataToDatabase(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail="Не удалось добавить запись"

class CannotAddToCart(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Не удалось добавить номер в корзину"

class InvalidTokenException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Invalid token"

class RequestAttorneyException(BookingException):
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    detail="Невалидный запрос"

class BookingMiss(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Бронирование с данным номером отсутствует"

class CartBookMiss(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Позиция с данным номером отсутствует в корзине"

class CannotCheckFav(BookingException):
    status_code=status.HTTP_400_BAD_REQUEST
    detail="Операция с избранным недоступна"

class PasswordNotConfirm(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Поля нового пароля не совпадают"