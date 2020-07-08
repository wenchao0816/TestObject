from django.http import JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
# 应该有专门的用户模块，这儿为了简化就不新建了
from .models import User
from django.views.generic.base import View


class ScoreView(View):
    def get(self, request):
        user_id = request.GET.get('user_id')
        page = request.GET.get('page')
        if user_id is None:
            return JsonResponse({'code': 201, 'errmsg': '用户信息信息有误，请核对后重新提交！'})
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'code': 202, 'errmsg': '用户未注册，请查证后再次提交'})
        try:
            page = int(page)
        except Exception as e:
            page = 1
        conn = get_redis_connection('default')
        info = conn.zrevrange('game1', 10**(page-1)-1, 10**(page-1)+9)
        res = []
        i = page
        user_info = []
        for key in info:
            key = key.decode()
            score = conn.zscore('game1', key)
            if key == user_id:
                user_info = [i, key, score]
            res.append([i, key, score])
            i += 1
        res.append(user_info)
        return JsonResponse({'code': 200, 'msg': '获取数据成功！', 'data': res})

    def post(self, request):
        user_id = request.POST.get('user_id')
        score = request.POST.get('score')
        if not all([user_id, score]):
            return JsonResponse({'code': 201, 'errmsg': '用户信息或输入分数信息有误，请核对后重新提交！'})
        # 核对是否存在该用户
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'code': 202, 'errmsg': '用户未注册，请查证后再次提交'})
        try:
            score = int(score)
        except Exception as e:
            return JsonResponse({'code': 203, 'errmsg': '输入分数有误，请核实后再次提交！'})
        conn = get_redis_connection('default')
        # 应该存取用户名的，目前没有数据库对应的用户信息，所以先存取用户id
        conn.zadd('game1', {user_id: score})
        return JsonResponse({'code': 200, 'msg': '数据保存成功！'})


# 返回验证模板文件
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
