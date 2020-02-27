# from django.db import models
#
#
# class Offer(models.Model):
#     title = models.CharField(max_length=128, null=True, blank=True, )
#     company_name = models.CharField(max_length=128, null=True, blank=True, )
#     company_url = models.URLField(null=True, blank=True, )
#     policy_name = models.CharField(max_length=128, null=True, blank=True, )
#     service_rating = models.SmallIntegerField(default=0)
#     ins_price = models.SmallIntegerField(default=0)
#
#
# class InfoItem(models.Model):
#     offer = models.ForeignKey(to=Offer, related_name='info', on_delete=models.CASCADE, )
#     header = models.TextField()
#     text = models.TextField()
#
#
# class BuildingOffer(Offer):
#     pass
#
#
# class ContentOffer(Offer):
#     pass
#
#
# class FullPropOffer(Offer):
#     pass
