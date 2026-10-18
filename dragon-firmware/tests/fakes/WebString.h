#pragma once
#include <string>
#include <type_traits>
#include <algorithm>
#include <cstring>
#include <cctype>
class String : public std::string {
public:
 using std::string::string;
 using std::string::operator=;
 bool concat(const char* text,size_t size){append(text,size);return true;}
 String():std::string(){} String(const std::string& x):std::string(x){}
 template<class T, typename std::enable_if<std::is_integral<T>::value,int>::type =0> String(T x):std::string(std::to_string(x)){}
 void toCharArray(char* out,size_t n)const{if(n){size_t len=std::min(n-1,size());memcpy(out,data(),len);out[len]=0;}}
 int indexOf(char c,int start=0)const{auto p=find(c,start);return p==npos?-1:int(p);}
 String substring(size_t start,size_t end)const{return substr(start,end-start);}
 void trim(){auto a=find_first_not_of(" \t\r\n"),b=find_last_not_of(" \t\r\n");*this=a==npos?String():String(substr(a,b-a+1));}
 bool equalsIgnoreCase(const char* text)const{String other(text);if(size()!=other.size())return false;for(size_t i=0;i<size();i++)if(tolower((*this)[i])!=tolower(other[i]))return false;return true;}
};
