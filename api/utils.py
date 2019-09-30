

class APIUtils():

    @staticmethod
    def extract_limit_offset(request):
        limit = 20
        offset = 0
        try:
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
        except Exception as e:
            pass
        return limit, offset
