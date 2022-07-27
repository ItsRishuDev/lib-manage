from dataclasses import field
from rest_framework import serializers

from library.models import Book, IssuedBook, SubmissionDetail
from account.serializers import ShowUserSerializer

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

        def create(self, validated_data):
            book = Book.objects.create(**validated_data)
            return book

        def update(self, instance, validated_data):
            instance.name = validated_data.get('name', instance.name)
            instance.author = validated_data.get('author', instance.author)  
            instance.edition = validated_data.get('edition', instance.edition)  
            instance.available = validated_data.get('available', instance.available)  
            instance.price = validated_data.get('price', instance.price)    
            instance.late_fee = validated_data.get('late_fee', instance.late_fee)  
            return instance


class IssuedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedBook
        fields = ('__all__')

        def create(self, validated_data):
            data = IssuedBook.objects.create(**validated_data)
            return data

        def update(self, instance, validated_data):
            instance.returned = validated_data.get('returned', instance.returned)
            return instance


class ShowIssuedBookSerializer(serializers.ModelSerializer):
    user = ShowUserSerializer()

    class Meta:
        model = IssuedBook
        fields = ['id', 'issue_date', 'returned', 'user', 'book']
        depth = 1


class SubmissionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionDetail
        fields = '__all__'

        def create(self, validated_data):
            data = SubmissionDetail.objects.create(**validated_data)