from fastapi import HTTPException


class SomethingGotWrongHTTPException(HTTPException):
    def __init__(
            self,
            status_code: int = 500,
            add_detail: str | None = None
    ):
        detail = "Something got wrong"
        if add_detail:
            detail += f": {add_detail}"
        super().__init__(status_code=status_code, detail=detail)