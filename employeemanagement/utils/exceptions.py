from rest_framework.exceptions import APIException


class CustomException(APIException):
    status_code = 400
    default_detail = "request error"
    default_code = "request_error"

    def __int__(self, detail=default_detail, status_code=status_code):
        self.detail = {"message": detail, "status_code": self.status_code}
